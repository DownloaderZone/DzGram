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
import bisect
import logging
import os
import time
from hashlib import sha1
from io import BytesIO
from typing import Any, Dict, List, Optional, Set

import pyrogram
from pyrogram import raw
from pyrogram.connection import Connection
from pyrogram.crypto import mtproto
from pyrogram.errors import (
    AuthKeyDuplicated,
    BadMsgNotification,
    FloodPremiumWait,
    FloodWait,
    InternalServerError,
    RPCError,
    SecurityCheckMismatch,
    ServiceUnavailable,
)
from pyrogram.raw.all import layer
from pyrogram.raw.core import FutureSalts, Int, Message, MsgContainer, TLObject

from .internals import MsgFactory, MsgId

log = logging.getLogger(__name__)

try:
    import warpcrypto

    _HAS_RUST_MSG = hasattr(warpcrypto, "pack_message") and hasattr(warpcrypto, "unpack_message")
except ImportError:
    warpcrypto = None  # type: ignore
    _HAS_RUST_MSG = False


class Result:
    __slots__ = ("value", "event")

    def __init__(self):
        self.value: Any = None
        self.event: asyncio.Event = asyncio.Event()


class ConnectionLost:
    pass


def _transport_error(packet: Optional[bytes]) -> Optional[str]:
    """Describe a packet too short to be a message, or None if it is one."""
    if packet is not None and len(packet) > 4:
        return None

    if not packet or len(packet) < 4:
        return "Connection closed by the server"

    error_code = -Int.read(BytesIO(packet))

    return "Server sent transport error: {}".format(error_code)


def _run_in_background(coro, loop: Optional[asyncio.AbstractEventLoop] = None):
    try:
        running = loop or asyncio.get_running_loop()
    except RuntimeError:
        running = None

    if running is not None:
        return running.create_task(coro)

    # Fallback for contexts without a running loop (e.g. sync wrapper threads).
    return asyncio.ensure_future(coro)


class Session:
    START_TIMEOUT = 2
    WAIT_TIMEOUT = 15
    MEDIA_WAIT_TIMEOUT = int(os.environ.get("DZGRAM_MEDIA_TIMEOUT", 60))
    SLEEP_THRESHOLD = 10
    MAX_RETRIES = 10
    ACKS_THRESHOLD = 10
    PING_INTERVAL = 5
    STORED_MSG_IDS_MAX_SIZE = 1000 * 2
    MAX_SKEW_AHEAD = 30
    MAX_SKEW_BEHIND = 300
    MAX_SKEW_BREACHES = 3
    MAX_INFLIGHT_PACKETS = int(os.environ.get("DZGRAM_MAX_INFLIGHT_PACKETS", 32))
    # Bounds concurrent invokes on a single media session. 0 (default) leaves
    # media sessions uncapped, matching historical throughput; set to a
    # positive value to throttle bursts per connection.
    MAX_INFLIGHT_MEDIA = int(os.environ.get("DZGRAM_MAX_INFLIGHT_MEDIA", 0))
    # Payloads at or below this size are encrypted inline; larger ones are
    # offloaded to the crypto executor so big transfer chunks don't stall
    # the event loop. Only applies when the Rust message crypto is present.
    INLINE_CRYPTO_MAX = int(os.environ.get("DZGRAM_INLINE_CRYPTO_MAX", 32 * 1024))

    CUR_ALWD_INNR_QRYS = (
        raw.functions.InvokeWithoutUpdates,
        raw.functions.InvokeWithTakeout,
        raw.functions.InvokeWithBusinessConnection,
    )

    def __init__(
        self,
        client: "pyrogram.Client",
        dc_id: int,
        auth_key: bytes,
        test_mode: bool,
        is_media: bool = False,
        is_cdn: bool = False,
        server_address: Optional[str] = None,
        port: Optional[int] = None,
    ):
        self.client = client
        self.dc_id = dc_id
        self.auth_key = auth_key
        self.test_mode = test_mode
        self.is_media = is_media
        self.is_cdn = is_cdn
        # Accepted for API compatibility with pooled-session factories.
        # Connection address resolution still lives in Connection/DataCenter.
        self.server_address = server_address
        self.port = port

        self.connection: Optional[Connection] = None

        self.auth_key_id = sha1(auth_key).digest()[-8:]

        self.session_id = os.urandom(8)
        self.msg_factory = MsgFactory()

        self.salt = 0

        self.pending_acks: Set[int] = set()

        self.results: Dict[int, Result] = {}

        self.stored_msg_ids: List[int] = []

        self._handler_lock = asyncio.Lock()
        self._packet_tasks = set()
        self._packet_semaphore = asyncio.Semaphore(Session.MAX_INFLIGHT_PACKETS)
        self._update_semaphore = asyncio.Semaphore(32)
        self._invoke_semaphore = (
            asyncio.Semaphore(Session.MAX_INFLIGHT_MEDIA)
            if (is_media and Session.MAX_INFLIGHT_MEDIA > 0)
            else None
        )

        self.ping_task: Optional[asyncio.Task] = None
        self.ping_task_event = asyncio.Event()

        self.recv_task: Optional[asyncio.Task] = None

        self.is_connected = asyncio.Event()
        # Newer alias used by pooled media sessions; kept in sync manually.
        self.is_started = self.is_connected

        self._restart_lock = asyncio.Lock()
        self._restart_done = asyncio.Event()
        self._restart_done.set()

        self._skew_breaches = 0
        self._msg_id_floor = 0
        self._teardown_started = False

        self._start_exc: Optional[BaseException] = None
        self._start_active = False
        self._start_completed = asyncio.Event()
        self._start_completed.set()
        self._stopping = False

        self.last_packet_received = 0.0
        self.last_used = time.monotonic()

    def _loop(self) -> asyncio.AbstractEventLoop:
        client_loop = getattr(self.client, "loop", None)

        if isinstance(client_loop, asyncio.AbstractEventLoop):
            return client_loop

        try:
            return asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.get_event_loop_policy().get_event_loop()

    async def start(self, max_attempts: Optional[int] = None):
        self._stopping = False
        self._start_exc = None
        self._start_active = True
        self._start_completed.clear()
        attempt = 0

        try:
            while True:
                attempt += 1
                self._stopping = False
                self._teardown_started = False
                self._skew_breaches = 0
                self._msg_id_floor = 0
                self.connection = Connection(
                    self.dc_id,
                    self.test_mode,
                    self.client.ipv6,
                    self.client.proxy,
                    self.is_media,
                )

                handshake_timeout = min(self.START_TIMEOUT * attempt, self.WAIT_TIMEOUT)

                try:
                    await self.connection.connect()

                    self.recv_task = self._loop().create_task(self.recv_worker())

                    await self.send(raw.functions.Ping(ping_id=0), timeout=handshake_timeout)

                    if not self.is_cdn:
                        await self.send(
                            raw.functions.InvokeWithLayer(
                                layer=layer,
                                query=raw.functions.InitConnection(
                                    api_id=await self.client.storage.api_id(),
                                    app_version=self.client.app_version,
                                    device_model=self.client.device_model,
                                    system_version=self.client.system_version,
                                    system_lang_code=self.client.lang_code,
                                    lang_code=self.client.lang_code,
                                    lang_pack="",
                                    query=raw.functions.help.GetConfig(),
                                    proxy=raw.types.InputClientProxy(
                                        address=self.client._un_docu_gnihts[0],
                                        port=self.client._un_docu_gnihts[1],
                                    ) if len(self.client._un_docu_gnihts) == 3 else None,
                                    params=self.client._un_docu_gnihts[2] if len(self.client._un_docu_gnihts) == 3 else None,
                                )
                            ),
                            timeout=handshake_timeout
                        )

                    self.ping_task = self._loop().create_task(self.ping_worker())

                    log.info("Session initialized: Pyrogram v%s (Layer %s)", pyrogram.__version__, layer)
                    log.info("Device: %s - %s", self.client.device_model, self.client.app_version)
                    log.info("System: %s (%s)", self.client.system_version, self.client.lang_code.upper())
                except AuthKeyDuplicated as e:
                    self._start_exc = e
                    await self.stop()
                    raise e
                except (FloodWait, FloodPremiumWait) as e:
                    await self.stop()

                    if max_attempts is not None and attempt >= max_attempts:
                        self._start_exc = e
                        raise

                    backoff = min(e.value, 30)
                    (log.warning if attempt >= 3 else log.debug)(
                        "Session start attempt %d flood-limited, retrying in %ss",
                        attempt, backoff
                    )
                    await asyncio.sleep(backoff)
                except (InternalServerError, ServiceUnavailable, TimeoutError, OSError) as e:
                    await self.stop()

                    if max_attempts is not None and attempt >= max_attempts:
                        self._start_exc = e
                        raise

                    backoff = min(2 ** (attempt - 1), 30)
                    (log.warning if attempt >= 3 else log.debug)(
                        "Session start attempt %d failed, retrying in %ss: %s",
                        attempt, backoff, str(e) or type(e).__name__
                    )
                    await asyncio.sleep(backoff)
                except RPCError as e:
                    self._start_exc = e
                    await self.stop()
                    raise
                except (Exception, asyncio.CancelledError) as e:
                    self._start_exc = e
                    await self.stop()
                    raise e
                else:
                    break

            self.is_connected.set()

            log.info("Session started")
        finally:
            self._start_active = False
            self._start_completed.set()

    async def stop(self):
        self.is_connected.clear()
        self._stopping = True

        self.ping_task_event.set()

        if self.ping_task is not None:
            try:
                await self.ping_task
            except (Exception, asyncio.CancelledError):
                pass

        self.ping_task_event.clear()

        if self.recv_task and self.recv_task is not asyncio.current_task():
            self.recv_task.cancel()
            try:
                await self.recv_task
            except (Exception, asyncio.CancelledError):
                pass

        for task in list(self._packet_tasks):
            task.cancel()
        if self._packet_tasks:
            await asyncio.gather(*self._packet_tasks, return_exceptions=True)
            self._packet_tasks.clear()

        self.stored_msg_ids.clear()
        self._msg_id_floor = 0

        if self.connection is not None:
            try:
                result = self.connection.close()
                if asyncio.iscoroutine(result):
                    await result
            except (Exception, asyncio.CancelledError):
                pass

        self._fail_pending()

        log.info("Session stopped")

    def _fail_pending(self, value=ConnectionLost):
        for result in self.results.values():
            if result.value is None:
                result.value = value
            result.event.set()

    @property
    def is_restarting(self) -> bool:
        return self._restart_lock.locked() or self._start_active

    async def restart(self):
        if self._restart_lock.locked():
            await self._restart_done.wait()
            return

        async with self._restart_lock:
            self._restart_done.clear()
            try:
                await self.stop()
                try:
                    if getattr(self.client.storage, "conn", True) is None:
                        await self.client.storage.open()
                except (Exception, asyncio.CancelledError):
                    pass
                await self.start(max_attempts=self.MAX_RETRIES)
            finally:
                self._restart_done.set()

    async def _teardown(self, reason: str):
        if self._teardown_started:
            return

        self._teardown_started = True

        log.warning("Discarding packet and closing connection: %s", reason)

        _run_in_background(self._safe_restart(), self._loop())

    async def handle_packet(self, packet):
        if _HAS_RUST_MSG:
            try:
                if len(packet) <= Session.INLINE_CRYPTO_MAX:
                    msg_id, seq_no, length, body_bytes, total_len = warpcrypto.unpack_message(
                        packet,
                        self.session_id,
                        self.auth_key,
                        self.auth_key_id
                    )
                else:
                    msg_id, seq_no, length, body_bytes, total_len = await self._loop().run_in_executor(
                        pyrogram.crypto_executor,
                        warpcrypto.unpack_message,
                        packet,
                        self.session_id,
                        self.auth_key,
                        self.auth_key_id
                    )
            except (Exception, asyncio.CancelledError) as e:
                log.warning("Failed to decrypt packet: %s %s", type(e).__name__, e)
                return

            try:
                # https://core.telegram.org/mtproto/security_guidelines#checking-message-length
                padding_len = total_len - 16 - length
                SecurityCheckMismatch.check(12 <= padding_len <= 1024, "12 <= len(padding) <= 1024")
                SecurityCheckMismatch.check(total_len % 4 == 0, "len(data) % 4 == 0")

                # https://core.telegram.org/mtproto/security_guidelines#checking-msg-id
                SecurityCheckMismatch.check(msg_id % 2 != 0, "message.msg_id % 2 != 0")
            except SecurityCheckMismatch as e:
                await self._teardown(str(e))
                return

            try:
                data = Message(TLObject.read(BytesIO(body_bytes)), msg_id, seq_no, length)
            except (Exception, asyncio.CancelledError) as e:
                log.warning("Failed to parse packet: %s %s", type(e).__name__, e)
                return
        else:
            try:
                data = await self._loop().run_in_executor(
                    pyrogram.crypto_executor,
                    mtproto.unpack,
                    BytesIO(packet),
                    self.session_id,
                    self.auth_key,
                    self.auth_key_id,
                )
            except SecurityCheckMismatch:
                return
            except (Exception, asyncio.CancelledError) as e:
                log.warning("Failed to decrypt packet: %s %s", type(e).__name__, e)
                return

        self.last_packet_received = time.monotonic()

        if self._teardown_started:
            return

        messages = (
            data.body.messages
            if isinstance(data.body, MsgContainer)
            else [data]
        )

        log.debug("Received: %s", data)

        for msg in messages:
            if msg.seq_no % 2 != 0:
                async with self._handler_lock:
                    if msg.msg_id not in self.pending_acks:
                        self.pending_acks.add(msg.msg_id)

            is_bad_notification = isinstance(
                msg.body, (raw.types.BadMsgNotification, raw.types.BadServerSalt)
            )

            if isinstance(msg.body, raw.types.BadServerSalt):
                self.salt = msg.body.new_server_salt

            rejected = is_bad_notification and msg.body.error_code in (16, 17)

            async with self._handler_lock:
                if rejected or not self.stored_msg_ids:
                    MsgId.sync(msg.msg_id, rejected)

                if len(self.stored_msg_ids) > Session.STORED_MSG_IDS_MAX_SIZE:
                    cut = Session.STORED_MSG_IDS_MAX_SIZE // 2
                    self._msg_id_floor = self.stored_msg_ids[cut - 1]
                    del self.stored_msg_ids[:cut]

                replayed = None
                skew = None

                if self.stored_msg_ids:
                    if msg.msg_id <= self._msg_id_floor:
                        replayed = "The msg_id is below the replay window"
                    else:
                        index = bisect.bisect_left(self.stored_msg_ids, msg.msg_id)

                        if index < len(self.stored_msg_ids) and self.stored_msg_ids[index] == msg.msg_id:
                            replayed = "The msg_id is equal to any of the stored values"

                    if replayed is None and not is_bad_notification:
                        time_diff = (msg.msg_id >> 32) - MsgId.now()

                        if time_diff > Session.MAX_SKEW_AHEAD or time_diff < -Session.MAX_SKEW_BEHIND:
                            skew = time_diff

                if replayed is not None:
                    log.debug("Discarding message: %s", replayed)
                    continue

                if skew is not None:
                    self._skew_breaches += 1

                    log.debug(
                        "Discarding message %ss out of step (%s/%s)",
                        int(skew), self._skew_breaches, Session.MAX_SKEW_BREACHES
                    )

                    if self._skew_breaches >= Session.MAX_SKEW_BREACHES:
                        self._skew_breaches = 0
                        MsgId.sync(msg.msg_id)

                        log.warning(
                            "Client clock is %ss out of step with the server; "
                            "time offset resynchronised to %.1fs",
                            int(skew), MsgId.time_offset
                        )

                    continue

                self._skew_breaches = 0
                bisect.insort(self.stored_msg_ids, msg.msg_id)

            if isinstance(msg.body, (raw.types.MsgDetailedInfo, raw.types.MsgNewDetailedInfo)):
                self.pending_acks.add(msg.body.answer_msg_id)
                continue

            if isinstance(msg.body, raw.types.NewSessionCreated):
                self.salt = msg.body.server_salt
                continue

            msg_id = None

            if is_bad_notification:
                msg_id = msg.body.bad_msg_id
            elif isinstance(msg.body, (FutureSalts, raw.types.RpcResult)):
                msg_id = msg.body.req_msg_id
            elif isinstance(msg.body, raw.types.Pong):
                msg_id = msg.body.msg_id
            else:
                if self.client is not None:
                    _run_in_background(self._run_update(msg.body), self._loop())

            if msg_id in self.results:
                self.results[msg_id].value = getattr(msg.body, "result", msg.body)
                self.results[msg_id].event.set()

        async with self._handler_lock:
            ack_ids = None
            if len(self.pending_acks) >= self.ACKS_THRESHOLD:
                ack_ids = list(self.pending_acks)
                self.pending_acks.clear()

        if ack_ids:
            log.debug("Sending %s acks", len(ack_ids))

            try:
                await self.send(raw.types.MsgsAck(msg_ids=ack_ids), False)
            except OSError:
                pass

    async def ping_worker(self):
        log.info("PingTask started")

        while True:
            try:
                await asyncio.wait_for(self.ping_task_event.wait(), self.PING_INTERVAL)
            except asyncio.TimeoutError:
                pass
            else:
                break

            try:
                await self.send(
                    raw.functions.PingDelayDisconnect(
                        ping_id=0,
                        disconnect_delay=self.WAIT_TIMEOUT + 10
                    ),
                    wait_response=False
                )

                await self.flush_acks()
            except (OSError, TimeoutError, RPCError):
                pass

        log.info("PingTask stopped")

    async def flush_acks(self):
        """Send whatever acks are owed, however few.

        handle_packet only flushes once ACKS_THRESHOLD of them pile up, so a link
        that goes quiet below that mark leaves them owed - and the server keeps
        re-delivering the updates they belong to for as long as the client runs.
        """
        async with self._handler_lock:
            if not self.pending_acks:
                return

            ack_ids = list(self.pending_acks)
            self.pending_acks.clear()

        log.debug("Sending %s acks", len(ack_ids))

        await self.send(raw.types.MsgsAck(msg_ids=ack_ids), False)

    async def _run_update(self, body):
        async with self._update_semaphore:
            await self.client.handle_updates(body)

    async def _handle_packet_wrapper(self, packet):
        task = asyncio.current_task()
        self._packet_tasks.add(task)
        try:
            await self.handle_packet(packet)
        except asyncio.CancelledError:
            pass
        except Exception:
            log.exception("Error handling packet")
        finally:
            self._packet_tasks.discard(task)

    async def recv_worker(self):
        log.info("NetworkTask started")

        while True:
            try:
                packet = await self.connection.recv()
            except TimeoutError:
                log.debug("Socket read timed out, continuing")
                continue
            except Exception as e:
                if self._teardown_started or self._stopping:
                    log.debug("Receive loop ending after a deliberate teardown")
                else:
                    log.exception("Error receiving packet")

                self._fail_pending(ConnectionResetError(str(e) or type(e).__name__))

                if self.is_connected.is_set():
                    await self._safe_restart()
                break

            reason = _transport_error(packet)

            if reason is not None:
                log.warning(reason)

                self._fail_pending(ConnectionResetError(reason))

                if self.is_connected.is_set():
                    await self._safe_restart()

                break

            if self._stopping:
                continue

            await self._packet_semaphore.acquire()

            if self._stopping:
                self._packet_semaphore.release()
                break

            task = self._loop().create_task(self._handle_packet_wrapper(packet))
            task.add_done_callback(lambda _: self._packet_semaphore.release())

        log.info("NetworkTask stopped")

    async def _safe_restart(self):
        try:
            await self.restart()
        except (Exception, asyncio.CancelledError) as e:
            log.error("Session restart failed: %s", e)

    async def send(
        self,
        data: TLObject,
        wait_response: bool = True,
        timeout: float = WAIT_TIMEOUT,
        retry: int = 0
    ):
        if self.connection is None:
            raise OSError("Connection is not established")

        serialized = data.write()
        message = self.msg_factory(data, len(serialized))
        msg_id = message.msg_id

        if wait_response:
            self.results[msg_id] = Result()

        log.debug("Sent: %s", message)

        payload = None

        if _HAS_RUST_MSG:
            if len(serialized) <= Session.INLINE_CRYPTO_MAX:
                try:
                    payload = warpcrypto.pack_message(
                        message.msg_id,
                        message.seq_no,
                        serialized,
                        self.salt,
                        self.session_id,
                        self.auth_key,
                        self.auth_key_id
                    )
                except (Exception, asyncio.CancelledError):
                    payload = None

            if payload is None:
                try:
                    payload = await self._loop().run_in_executor(
                        pyrogram.crypto_executor,
                        warpcrypto.pack_message,
                        message.msg_id,
                        message.seq_no,
                        serialized,
                        self.salt,
                        self.session_id,
                        self.auth_key,
                        self.auth_key_id
                    )
                except (Exception, asyncio.CancelledError):
                    payload = None

        if payload is None:
            payload = await self._loop().run_in_executor(
                pyrogram.crypto_executor,
                mtproto.pack,
                message,
                self.salt,
                self.session_id,
                self.auth_key,
                self.auth_key_id
            )

        delivered = False

        try:
            try:
                await asyncio.wait_for(
                    self.connection.send(payload), timeout or self.WAIT_TIMEOUT
                )
            except asyncio.TimeoutError:
                raise TimeoutError("Request send timed out")

            delivered = True
        finally:
            if wait_response and not delivered:
                self.results.pop(msg_id, None)

        if wait_response:
            try:
                try:
                    await asyncio.wait_for(self.results[msg_id].event.wait(), timeout)
                except asyncio.TimeoutError:
                    pass
            finally:
                result = self.results.pop(msg_id, None)
                result = result.value if result is not None else None

            if result is ConnectionLost:
                raise ConnectionResetError("Connection lost while awaiting a response")

            if isinstance(result, BaseException):
                raise ConnectionResetError(str(result))

            if result is None:
                raise TimeoutError

            if isinstance(result, raw.types.RpcError):
                if isinstance(data, Session.CUR_ALWD_INNR_QRYS):
                    data = data.query

                RPCError.raise_it(result, type(data))

            if isinstance(result, raw.types.BadMsgNotification):
                log.warning(
                    "%s: %s", BadMsgNotification.__name__, BadMsgNotification(result.error_code)
                )

                if retry > 1:
                    raise BadMsgNotification(result.error_code)
                return await self.send(data, wait_response, timeout, retry + 1)

            if isinstance(result, raw.types.BadServerSalt):
                self.salt = result.new_server_salt
                if retry > 3:
                    raise BadMsgNotification(getattr(result, "error_code", 0))
                return await self.send(data, wait_response, timeout, retry + 1)

            return result

    async def _wait_started(self):
        if self._start_active:
            await self._start_completed.wait()

        if not self.is_connected.is_set():
            await self.restart()

        if not self.is_connected.is_set() and self._start_exc is not None:
            raise self._start_exc

    async def invoke(
        self,
        query: TLObject,
        retries: int = MAX_RETRIES,
        timeout: float = WAIT_TIMEOUT,
        sleep_threshold: float = SLEEP_THRESHOLD
    ):
        self.last_used = time.monotonic()

        if self._invoke_semaphore is None:
            return await self._invoke(query, retries, timeout, sleep_threshold)

        async with self._invoke_semaphore:
            return await self._invoke(query, retries, timeout, sleep_threshold)

    async def _invoke(
        self,
        query: TLObject,
        retries: int,
        timeout: float,
        sleep_threshold: float
    ):
        # Client-level sleep_threshold overrides the default when provided.
        try:
            client_threshold = self.client.sleep_threshold
        except AttributeError:
            client_threshold = None

        if client_threshold is not None:
            sleep_threshold = max(sleep_threshold, client_threshold)

        slept = 0.0
        flood_budget = (
            sleep_threshold * Session.MAX_RETRIES
            if sleep_threshold is not None and sleep_threshold >= 0
            else 0.0
        )

        while retries > 0:
            if not self.is_connected.is_set():
                await self._wait_started()

            if isinstance(query, Session.CUR_ALWD_INNR_QRYS):
                inner_query = query.query
            else:
                inner_query = query

            query_name = ".".join(inner_query.QUALNAME.split(".")[1:])

            try:
                return await self.send(query, timeout=timeout)
            except (FloodWait, FloodPremiumWait) as e:
                amount = e.value

                if amount > sleep_threshold >= 0:
                    raise

                if sleep_threshold >= 0 and slept + amount > flood_budget:
                    raise

                slept += amount

                log.warning(
                    '[%s] Waiting for %s seconds before continuing (required by "%s")',
                    self.client.name,
                    amount,
                    query_name,
                )

                await asyncio.sleep(amount)
            except (OSError, TimeoutError, InternalServerError, ServiceUnavailable) as e:
                # Some server-side 500s are not transient for this query; don't
                # burn the whole retry budget on them.
                if (
                    isinstance(e, InternalServerError)
                    and getattr(e, "code", 0) == 500
                    and (getattr(e, "ID", None) or getattr(e, "NAME", None)) in [
                        "HISTORY_GET_FAILED",
                        "PERSISTENT_TIMESTAMP_OUTDATED",
                    ]
                ):
                    raise e from None

                retries -= 1
                if retries == 0:
                    raise

                (log.warning if retries < 2 else log.info)(
                    '[%s] Retrying "%s" (attempt %s/%s) due to: %s',
                    self.client.name, query_name,
                    Session.MAX_RETRIES - retries, Session.MAX_RETRIES,
                    str(e) or repr(e)
                )

                if isinstance(e, ConnectionResetError):
                    await asyncio.sleep(0.1)
                elif isinstance(e, (InternalServerError, ServiceUnavailable)) or (
                    isinstance(e, TimeoutError)
                    and time.monotonic() - self.last_packet_received < self.WAIT_TIMEOUT
                ):
                    await asyncio.sleep(1)
                else:
                    await self.restart()

        raise TimeoutError("Exceeded maximum number of retries")

    def __str__(self) -> str:
        return (
            f"Session(dc_id={self.dc_id}, test_mode={self.test_mode}, "
            f"is_media={self.is_media}, is_cdn={self.is_cdn})"
        )
