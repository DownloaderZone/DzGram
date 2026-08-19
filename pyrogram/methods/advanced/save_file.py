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
from typing import Union, Callable

import pyrogram
from pyrogram import StopTransmission
from pyrogram import raw
from pyrogram.errors import RPCError
from pyrogram.methods.rate_limiter import TokenBucket
from pyrogram.session import Session
from pyrogram.transfer import ReadAhead

log = logging.getLogger(__name__)

PART_SIZE = 512 * 1024
POOL_SIZE = 20
MAX_RETRIES = 5
STALL_TIMEOUT = 900
READ_BUFFER = 4 * 1024 * 1024
MAX_BATCH = 4 * 1024 * 1024
PROGRESS_INTERVAL = 0.2


class SaveFile:
    async def save_file(
        self: "pyrogram.Client",
        path: Union[str, "io.BytesIO"],
        file_id: int = None,
        file_part: int = 0,
        progress: Callable = None,
        progress_args: tuple = ()
    ):
        """Upload a file onto Telegram servers, without actually sending the message to anyone.
        Useful whenever an InputFile type is required.

        .. note::

            This is a utility method intended to be used **only** when working with raw
            :obj:`functions <pyrogram.raw.functions>` (i.e: a Telegram API method you wish to use which is not
            available yet in the Client class as an easy-to-use method).

        Parameters:
            path (``str`` | :obj:`io.BytesIO`):
                The path of the file you want to upload that exists on your local machine or a binary file-like object
                with its attribute ".name" set for in-memory uploads.

            file_id (``int``, *optional*):
                In case a file part expired, pass the file_id and the file_part to retry uploading that specific chunk.

            file_part (``int``, *optional*):
                In case a file part expired, pass the file_id and the file_part to retry uploading that specific chunk.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.
                The function must take *(current, total)* as positional arguments (look at Other Parameters below for a
                detailed description) and will be called back each time a new file chunk has been successfully
                transmitted.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.
                You can pass anything you need to be available in the progress callback scope; for example, a Message
                object or a Client instance in order to edit the message with the updated progress status.

        Other Parameters:
            current (``int``):
                The amount of bytes transmitted so far.

            total (``int``):
                The total size of the file.

            *args (``tuple``, *optional*):
                Extra custom arguments as defined in the ``progress_args`` parameter.
                You can either keep ``*args`` or add every single extra argument in your function signature.

        Returns:
            :obj:`~pyrogram.raw.base.InputFile`: On success, the uploaded file is returned in form of an InputFile object.

        Raises:
            :obj:`~pyrogram.errors.RPCError`: In case of a Telegram RPC error.

        """
        async with self.save_file_semaphore:
            if path is None:
                return None

            async def worker(session):
                while True:
                    data = await queue.get()

                    if data is None:
                        return

                    try:
                        await send_part(session, data)
                    finally:
                        data = None
                        budget.release()

            async def send_part(session, data):
                for attempt in range(MAX_RETRIES):
                    try:
                        await session.invoke(
                            data, timeout=Session.MEDIA_WAIT_TIMEOUT
                        )
                        break
                    except StopTransmission:
                        raise
                    except (OSError, TimeoutError, RPCError, asyncio.TimeoutError) as e:
                        if attempt == MAX_RETRIES - 1:
                            log.exception("Upload part failed after %d attempts", MAX_RETRIES)
                            raise

                        delay = min(2 ** attempt, 30)
                        err_str = str(e)

                        if "FLOOD" in err_str:
                            for part in err_str.split():
                                if part.isdigit():
                                    delay = min(int(part), 300)
                                    break

                        log.warning(
                            "Retrying upload part (attempt %d/%d): %s",
                            attempt + 1, MAX_RETRIES, err_str[:120],
                        )
                        await asyncio.sleep(delay)

            async def read_batch():
                batch_size = min(PART_SIZE * n_workers, MAX_BATCH)

                return await self.loop.run_in_executor(
                    self.executor, fp.read, batch_size
                )

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

            # TODO
            file_size_limit_mib = 4000 if (self.me and self.me.is_premium) else 2000

            if file_size > file_size_limit_mib * 1024 * 1024:
                raise ValueError(f"Can't upload files bigger than {file_size_limit_mib} MiB")

            file_total_parts = int(math.ceil(file_size / part_size))
            is_big = file_size > 10 * 1024 * 1024
            is_bot = self.me.is_bot if self.me else False
            is_premium = self.me.is_premium if self.me else False

            if self.upload_workers is not None:
                rate_limit = 50
                pool_size = min(self.upload_workers, POOL_SIZE) if is_big else 1
            elif is_bot:
                rate_limit = 40  # ~20 MiB/s
                pool_size = min(8, POOL_SIZE) if is_big else 1
            elif is_premium:
                rate_limit = 300
                pool_size = min(14, POOL_SIZE) if is_big else 1
            else:
                rate_limit = 50  # ~25 MiB/s
                pool_size = min(12, POOL_SIZE) if is_big else 1

            is_missing_part = file_id is not None
            file_id = file_id or self.rnd_id()
            md5_sum = md5() if not is_big and not is_missing_part else None

            dc_id = await self.storage.dc_id()
            pool = await self._get_media_session_pool(dc_id, pool_size)

            n_workers = len(pool) * 2
            queue = asyncio.Queue(n_workers)
            budget = ReadAhead(self.read_ahead_slots)
            workers = [
                self.loop.create_task(worker(pool[i % len(pool)]))
                for i in range(n_workers)
            ]
            next_batch_task = None
            _last_progress_time = 0.0
            _next_dispatch = 0.0
            _dispatch_interval = 1.0 / rate_limit
            _stalled_since = 0.0

            progress_task = None

            if progress:
                async def progress_reporter():
                    nonlocal _last_progress_time

                    try:
                        prev_part = 0

                        while True:
                            await asyncio.sleep(0.5)
                            p = file_part

                            if p == 0 or p == prev_part:
                                continue

                            prev_part = p
                            now = time.monotonic()

                            if now - _last_progress_time >= PROGRESS_INTERVAL:
                                _last_progress_time = now
                                s = min(p * part_size, file_size)

                                try:
                                    if inspect.iscoroutinefunction(progress):
                                        await progress(s, file_size, *progress_args)
                                    else:
                                        await self.loop.run_in_executor(
                                            self.executor,
                                            functools.partial(
                                                progress, s, file_size, *progress_args
                                            ),
                                        )
                                except pyrogram.StopTransmission:
                                    raise
                                except Exception as e:
                                    log.warning(f"Progress callback error: {e}")
                    except asyncio.CancelledError:
                        pass

                progress_task = asyncio.ensure_future(progress_reporter())

            async def check_workers():
                for t in workers + ([progress_task] if progress_task else []):
                    if t.done():
                        exc = t.exception()

                        if exc is not None and not isinstance(exc, asyncio.CancelledError):
                            raise exc

            try:
                fp.seek(part_size * file_part)
                next_batch_task = self.loop.create_task(read_batch())

                while True:
                    batch = await next_batch_task
                    next_batch_task = self.loop.create_task(read_batch())

                    if not batch:
                        next_batch_task.cancel()
                        next_batch_task = None

                        if not is_big and not is_missing_part:
                            md5_sum = md5_sum.hexdigest()
                        break

                    await check_workers()

                    for start in range(0, len(batch), part_size):
                        chunk = batch[start:start + part_size]

                        if is_big:
                            rpc = raw.functions.upload.SaveBigFilePart(
                                file_id=file_id,
                                file_part=file_part,
                                file_total_parts=file_total_parts,
                                bytes=chunk
                            )
                        else:
                            rpc = raw.functions.upload.SaveFilePart(
                                file_id=file_id,
                                file_part=file_part,
                                bytes=chunk
                            )

                        _now = time.monotonic()

                        if _now < _next_dispatch:
                            await asyncio.sleep(_next_dispatch - _now)

                        _next_dispatch = max(time.monotonic(), _next_dispatch) + _dispatch_interval

                        await budget.acquire()
                        await check_workers()

                        while True:
                            try:
                                await asyncio.wait_for(queue.put(rpc), timeout=30)
                                _stalled_since = 0.0
                                break
                            except asyncio.TimeoutError:
                                await check_workers()

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
                            next_batch_task = None

                            for _ in range(n_workers):
                                await queue.put(None)

                            results = await asyncio.gather(*workers, return_exceptions=True)

                            for r in results:
                                if isinstance(r, BaseException) and not isinstance(
                                    r, asyncio.CancelledError
                                ):
                                    raise r

                            return None

                        if not is_big and not is_missing_part:
                            md5_sum.update(chunk)

                        rpc = None
                        chunk = None
                        file_part += 1

                    batch = None

            except StopTransmission:
                raise
            except Exception as e:
                log.exception(e)
                raise
            else:
                for _ in range(n_workers):
                    await queue.put(None)

                results = await asyncio.gather(*workers, return_exceptions=True)

                for r in results:
                    if isinstance(r, BaseException) and not isinstance(
                        r, asyncio.CancelledError
                    ):
                        raise r

                if progress and not is_missing_part:
                    # Report the final progress once every part has been sent.
                    _last_progress_time = 0.0

                    try:
                        if inspect.iscoroutinefunction(progress):
                            await progress(file_size, file_size, *progress_args)
                        else:
                            await self.loop.run_in_executor(
                                self.executor,
                                functools.partial(
                                    progress, file_size, file_size, *progress_args
                                ),
                            )
                    except pyrogram.StopTransmission:
                        raise
                    except Exception as e:
                        log.warning(f"Progress callback error: {e}")

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
                        md5_checksum=md5_sum
                    )
            finally:
                if progress_task and not progress_task.done():
                    progress_task.cancel()

                if next_batch_task is not None and not next_batch_task.done():
                    next_batch_task.cancel()

                for _ in range(n_workers):
                    try:
                        await asyncio.wait_for(queue.put(None), 2)
                    except asyncio.TimeoutError:
                        break

                for t in workers:
                    if not t.done():
                        t.cancel()

                await asyncio.gather(*workers, return_exceptions=True)
                budget.release_all()

                if isinstance(path, (str, PurePath)):
                    fp.close()