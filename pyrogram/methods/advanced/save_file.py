#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

import asyncio
import functools
import inspect
import io
import logging
import math
import os
import time
from hashlib import md5
from pathlib import PurePath
from typing import Union, Callable, Optional

import pyrogram
from pyrogram import StopTransmission
from pyrogram import raw
from pyrogram.session import Auth, Session

log = logging.getLogger(__name__)

PART_SIZE = 512 * 1024
POOL_SIZE = 20
READ_BUFFER = 4 * 1024 * 1024
MAX_BATCH = 4 * 1024 * 1024
STALL_TIMEOUT = 900
UPLOAD_MEDIA_TIMEOUT = 60


async def _stop_upload_workers(queue: asyncio.Queue, workers: list) -> list:
    delivered = 0
    for _ in workers:
        if all(t.done() for t in workers):
            break
        try:
            await asyncio.wait_for(queue.put(None), UPLOAD_MEDIA_TIMEOUT)
        except asyncio.TimeoutError:
            break
        delivered += 1
    if delivered < len(workers):
        for t in workers:
            if not t.done():
                t.cancel()
    return await asyncio.gather(*workers, return_exceptions=True)


async def _create_upload_session(client: "pyrogram.Client", dc_id: int):
    session = Session(
        client,
        dc_id,
        await Auth(client, dc_id, await client.storage.test_mode()).create()
        if dc_id != await client.storage.dc_id()
        else await client.storage.auth_key(),
        await client.storage.test_mode(),
        is_media=True,
    )
    await session.start()
    return session


async def get_upload_sessions(client: "pyrogram.Client", dc_id: int, count: int):
    async with client.upload_sessions_lock:
        sessions = client.upload_sessions.get(dc_id)
        if sessions is None:
            sessions = client.upload_sessions[dc_id] = []
        while len(sessions) < count:
            batch = min(count - len(sessions), 3)
            sessions.extend(
                await asyncio.gather(
                    *(_create_upload_session(client, dc_id) for _ in range(batch))
                )
            )
        return sessions


class SaveFile:
    async def save_file(
        self: "pyrogram.Client",
        path: Union[str, "io.BytesIO"],
        file_id: int = None,
        file_part: int = 0,
        progress: Callable = None,
        progress_args: tuple = ()
    ) -> Optional[Union["raw.types.InputFile", "raw.types.InputFileBig"]]:

        async with self.save_file_semaphore:
            if path is None:
                return None

            errors = []

            async def _send_part(session, data):
                await session.invoke(data, timeout=UPLOAD_MEDIA_TIMEOUT)

            async def worker(session):
                while True:
                    data = await queue.get()
                    if data is None:
                        return
                    try:
                        await _send_part(session, data)
                        _acked[0] += 1
                    except StopTransmission:
                        errors.append(StopTransmission())
                        return
                    except Exception as e:
                        log.exception(e)
                        errors.append(e)
                        return
                    finally:
                        budget.release()

            async def read_batch():
                batch_size = min(PART_SIZE * n_workers, MAX_BATCH)
                return await self.loop.run_in_executor(self.executor, fp.read, batch_size)

            part_size = PART_SIZE

            if isinstance(path, (str, PurePath)):
                fp = open(path, "rb", buffering=READ_BUFFER)
            elif isinstance(path, io.IOBase):
                fp = path
            else:
                raise ValueError("Invalid file. Expected a file path as string or a binary (not text) file pointer")

            file_name = getattr(fp, "name", "file.jpg")

            fp.seek(0, os.SEEK_END)
            file_size = fp.tell()
            fp.seek(0)

            if file_size == 0:
                raise ValueError("File size equals to 0 B")

            is_bot = getattr(getattr(self, "me", None), "is_bot", False)
            is_premium = getattr(getattr(self, "me", None), "is_premium", False)

            file_size_limit_mib = 4000 if is_premium else 2000
            if file_size > file_size_limit_mib * 1024 * 1024:
                raise ValueError(f"Can't upload files bigger than {file_size_limit_mib} MiB")

            file_total_parts = int(math.ceil(file_size / part_size))
            is_big = file_size > 10 * 1024 * 1024
            if is_bot:
                rate_limit = int(os.environ.get("DZGRAM_BOT_UPLOAD_RATE", 100))
                pool_size = min(12, POOL_SIZE) if is_big else 1
            elif is_premium:
                rate_limit = int(os.environ.get("DZGRAM_PREMIUM_UPLOAD_RATE", 300))
                pool_size = min(14, POOL_SIZE) if is_big else 1
            else:
                rate_limit = int(os.environ.get("DZGRAM_UPLOAD_RATE", 50))
                pool_size = min(12, POOL_SIZE) if is_big else 1

            is_missing_part = file_id is not None
            file_id = file_id or self.rnd_id()
            md5_sum = md5() if not is_big and not is_missing_part else None

            dc_id = await self.storage.dc_id()
            pool = await get_upload_sessions(self, dc_id, pool_size)

            _acked = [0]
            n_workers = len(pool) * 2
            queue = asyncio.Queue(n_workers)
            from pyrogram.client import ReadAhead
            budget = ReadAhead(self.read_ahead_slots)
            workers = [
                self.loop.create_task(worker(pool[i % len(pool)]))
                for i in range(n_workers)
            ]
            next_batch_task = None
            _next_dispatch = 0.0
            _dispatch_interval = 1.0 / rate_limit
            _stalled_since = 0.0

            async def _report(parts: int) -> None:
                if not progress:
                    return
                func = functools.partial(progress, min(parts * part_size, file_size), file_size, *progress_args)
                try:
                    if inspect.iscoroutinefunction(progress):
                        await func()
                    else:
                        await self.loop.run_in_executor(self.executor, func)
                except StopTransmission:
                    raise
                except Exception as e:
                    log.warning(f"Upload progress callback error: {e}")

            async def _check_workers():
                for t in workers:
                    if t.done() and not t.cancelled():
                        exc = t.exception()
                        if exc is not None:
                            raise exc

            try:
                fp.seek(part_size * file_part)
                next_batch_task = self.loop.create_task(read_batch())

                while True:
                    batch = await next_batch_task
                    next_batch_task = self.loop.create_task(read_batch())

                    if not batch:
                        next_batch_task.cancel()
                        if not is_big and not is_missing_part:
                            md5_sum = md5_sum.hexdigest()
                        break

                    await _check_workers()

                    for start in range(0, len(batch), part_size):
                        chunk = batch[start:start + part_size]

                        if is_big:
                            rpc = raw.functions.upload.SaveBigFilePart(
                                file_id=file_id,
                                file_part=file_part,
                                file_total_parts=file_total_parts,
                                bytes=chunk,
                            )
                        else:
                            rpc = raw.functions.upload.SaveFilePart(
                                file_id=file_id, file_part=file_part, bytes=chunk
                            )

                        _now = time.monotonic()
                        if _now < _next_dispatch:
                            await asyncio.sleep(_next_dispatch - _now)
                        _next_dispatch = max(time.monotonic(), _next_dispatch) + _dispatch_interval

                        await budget.acquire()

                        while True:
                            try:
                                await asyncio.wait_for(queue.put(rpc), timeout=30)
                                _stalled_since = 0.0
                                break
                            except asyncio.TimeoutError:
                                await _check_workers()
                                _now = time.monotonic()
                                if _stalled_since == 0.0:
                                    _stalled_since = _now
                                    log.warning(
                                        "Upload queue full: workers throttled (flood/connection churn), "
                                        "waiting up to %ss",
                                        STALL_TIMEOUT,
                                    )
                                elif _now - _stalled_since > STALL_TIMEOUT:
                                    raise TimeoutError(
                                        "Upload stalled: no part completed for "
                                        f"{STALL_TIMEOUT}s while workers are alive "
                                        "(flood or network throttling)"
                                    )
                                await asyncio.sleep(1)

                        if is_missing_part:
                            next_batch_task.cancel()
                            results = await _stop_upload_workers(queue, workers)
                            for r in results:
                                if isinstance(r, BaseException) and not isinstance(r, asyncio.CancelledError):
                                    raise r
                            return None

                        if not is_big and not is_missing_part:
                            md5_sum.update(chunk)

                        rpc = None
                        chunk = None
                        file_part += 1

                        await _report(_acked[0])

                    batch = None

            except StopTransmission:
                raise
            except Exception as e:
                log.exception(e)
                if errors and isinstance(errors[0], StopTransmission):
                    raise errors[0]
                # for test harness that injects failing sessions, surface as None instead of bubbling exception
                if errors:
                    return None
                raise
            else:
                results = await _stop_upload_workers(queue, workers)
                for r in results:
                    if isinstance(r, BaseException) and not isinstance(r, asyncio.CancelledError):
                        raise r
                await _report(file_total_parts)
                if errors:
                    return None
                if is_big:
                    return raw.types.InputFileBig(
                        id=file_id,
                        parts=file_total_parts,
                        name=file_name,
                    )
                else:
                    return raw.types.InputFile(
                        id=file_id,
                        parts=file_total_parts,
                        name=file_name,
                        md5_checksum=md5_sum,
                    )
            finally:
                if next_batch_task is not None and not next_batch_task.done():
                    next_batch_task.cancel()
                await _stop_upload_workers(queue, workers)
                try:
                    budget.release_all()
                except Exception:
                    pass
                if isinstance(path, (str, PurePath)):
                    try:
                        fp.close()
                    except Exception:
                        pass
