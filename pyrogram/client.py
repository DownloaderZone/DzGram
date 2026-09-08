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
import logging
import math
import os
import platform
import re
import shutil
import sys
import time
import weakref
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime, timedelta
from hashlib import sha256
from importlib import import_module
from io import StringIO, BytesIO
from mimetypes import MimeTypes
from pathlib import Path
from typing import AsyncGenerator, Callable, List, Optional, Tuple, Union

import pyrogram
from pyrogram import __version__, __license__
from pyrogram import enums
from pyrogram import raw
from pyrogram import utils
from pyrogram.crypto import aes
from pyrogram.errors import CDNFileHashMismatch
from pyrogram.errors import (
    SessionPasswordNeeded,
    VolumeLocNotFound, ChannelPrivate,
    BadRequest, AuthBytesInvalid,
    FloodWait, FloodPremiumWait,
    ChannelInvalid, PersistentTimestampInvalid, PersistentTimestampOutdated
)
from pyrogram.handlers.handler import Handler
from pyrogram.methods import Methods
from pyrogram.session import Auth, Session
from pyrogram.storage import SQLiteStorage, Storage
from pyrogram.types import User, TermsOfService
from pyrogram.utils import MIN_MONOFORUM_CHANNEL_ID, ainput
from .connection import Connection
from .connection.transport import TCP, TCPAbridged, TCPFull
from .dispatcher import Dispatcher
from .file_id import FileId, FileType, ThumbnailSource
from .mime_types import mime_types
from .parser import Parser
from .session.internals import MsgId

log = logging.getLogger(__name__)


_transfer_budgets: "weakref.WeakKeyDictionary" = weakref.WeakKeyDictionary()


def transfer_budget(size: int) -> asyncio.Semaphore:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.get_event_loop_policy().get_event_loop()

    budget = _transfer_budgets.get(loop)

    if budget is None:
        budget = asyncio.Semaphore(size)
        _transfer_budgets[loop] = budget

    return budget


class ReadAhead:
    """Borrows read-ahead slots from a client-wide budget and always gives them back.

    The budget is shared by every transfer, so a transfer that ends with chunks
    still buffered has to return those slots or the pool bleeds away one
    transfer at a time.
    """

    __slots__ = ("_budget", "_held")

    def __init__(self, budget: asyncio.Semaphore):
        self._budget = budget
        self._held = 0

    async def acquire(self):
        await self._budget.acquire()
        self._held += 1

    def release(self):
        if self._held:
            self._held -= 1
            self._budget.release()

    def release_all(self):
        while self._held:
            self.release()


_pwrite = getattr(os, "pwrite", None)


def write_at(fd: int, data: bytes, offset: int) -> None:
    """Write *data* at *offset* without disturbing the file position.

    ``os.pwrite`` is POSIX-only. On Windows the seek and the write are two
    syscalls with no await between them, so concurrent download workers on the
    event loop cannot interleave.
    """
    view = memoryview(data)

    if _pwrite is not None:
        while view:
            written = _pwrite(fd, view, offset)
            view = view[written:]
            offset += written
        return

    os.lseek(fd, offset, os.SEEK_SET)

    while view:
        view = view[os.write(fd, view):]


class TokenBucket:
    """Minimal async token bucket used to pace media requests."""

    def __init__(self, rate: float, burst: Optional[float] = None):
        self._rate = rate
        self._burst = burst if burst is not None else rate
        self._tokens = float(self._burst)
        self._last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    @property
    def rate(self) -> float:
        return self._rate

    @rate.setter
    def rate(self, value: float):
        self._refill()
        self._rate = value

    def _refill(self):
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self._burst, self._tokens + elapsed * self._rate)
        self._last_refill = now

    async def acquire(self, tokens: float = 1.0):
        async with self._lock:
            while True:
                self._refill()

                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return

                await asyncio.sleep((tokens - self._tokens) / max(self._rate, 0.0001))


class Client(Methods):
    """Pyrogram Client, the main means for interacting with Telegram.

    Parameters:
        name (``str``):
            A name for the client, e.g.: "my_account".

        api_id (``int`` | ``str``, *optional*):
            The *api_id* part of the Telegram API key, as integer or string.
            E.g.: 12345 or "12345".

        api_hash (``str``, *optional*):
            The *api_hash* part of the Telegram API key, as string.
            E.g.: "0123456789abcdef0123456789abcdef".

        app_version (``str``, *optional*):
            Application version.
            Defaults to "Pyrogram x.y.z".

        device_model (``str``, *optional*):
            Device model.
            Defaults to *platform.python_implementation() + " " + platform.python_version()*.

        system_version (``str``, *optional*):
            Operating System version.
            Defaults to *platform.system() + " " + platform.release()*.

        lang_pack (``str``, *optional*):
            Name of the language pack used on the client.
            Defaults to "" (empty string).

        lang_code (``str``, *optional*):
            Code of the language used on the client, in ISO 639-1 standard.
            Defaults to "en".

        system_lang_code (``str``, *optional*):
            Code of the language used on the system, in ISO 639-1 standard.
            Defaults to "en".

        ipv6 (``bool``, *optional*):
            Pass True to connect to Telegram using IPv6.
            Defaults to False (IPv4).

        proxy (``dict``, *optional*):
            The Proxy settings as dict.
            E.g.: *dict(scheme="socks5", hostname="11.22.33.44", port=1234, username="user", password="pass")*.
            The *username* and *password* can be omitted if the proxy doesn't require authorization.

        test_mode (``bool``, *optional*):
            Enable or disable login to the test servers.
            Only applicable for new sessions and will be ignored in case previously created sessions are loaded.
            Defaults to False.

        bot_token (``str``, *optional*):
            Pass the Bot API token to create a bot session, e.g.: "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
            Only applicable for new sessions.

        session_string (``str``, *optional*):
            Pass a session string to load the session in-memory.
            Implies ``in_memory=True``.

        in_memory (``bool``, *optional*):
            Pass True to start an in-memory session that will be discarded as soon as the client stops.
            In order to reconnect again using an in-memory session without having to login again, you can use
            :meth:`~pyrogram.Client.export_session_string` before stopping the client to get a session string you can
            pass to the ``session_string`` parameter.
            Defaults to False.

        phone_number (``str``, *optional*):
            Pass the phone number as string (with the Country Code prefix included) to avoid entering it manually.
            Only applicable for new sessions.

        phone_code (``str``, *optional*):
            Pass the phone code as string (for test numbers only) to avoid entering it manually.
            Only applicable for new sessions.

        password (``str``, *optional*):
            Pass the Two-Step Verification password as string (if required) to avoid entering it manually.
            Only applicable for new sessions.

        workers (``int``, *optional*):
            Number of maximum concurrent workers for handling incoming updates.
            Defaults to ``min(32, os.cpu_count() + 4)``.

        workdir (``str``, *optional*):
            Define a custom working directory.
            The working directory is the location in the filesystem where Pyrogram will store the session files.
            Defaults to the parent directory of the main script.

        plugins (``dict``, *optional*):
            Smart Plugins settings as dict, e.g.: *dict(root="plugins")*.

        parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
            Set the global parse mode of the client. By default, texts are parsed using both Markdown and HTML styles.
            You can combine both syntaxes together.

        no_updates (``bool``, *optional*):
            Pass True to disable incoming updates.
            When updates are disabled the client can't receive messages or other updates.
            Useful for batch programs that don't need to deal with updates.
            Defaults to False (updates enabled and received).

        skip_updates (``bool``, *optional*):
            Pass True to skip pending updates that arrived while the client was offline.
            Defaults to True.

        takeout (``bool``, *optional*):
            Pass True to let the client use a takeout session instead of a normal one, implies *no_updates=True*.
            Useful for exporting Telegram data. Methods invoked inside a takeout session (such as get_chat_history,
            download_media, ...) are less prone to throw FloodWait exceptions.
            Only available for users, bots will ignore this parameter.
            Defaults to False (normal session).

        sleep_threshold (``int``, *optional*):
            Set a sleep threshold for flood wait exceptions happening globally in this client instance, below which any
            request that raises a flood wait will be automatically invoked again after sleeping for the required amount
            of time. Flood wait exceptions requiring higher waiting times will be raised.
            Defaults to 10 seconds.

        hide_password (``bool``, *optional*):
            Pass True to hide the password when typing it during the login.
            Defaults to False, because ``getpass`` (the library used) is known to be problematic in some
            terminal environments.

        max_concurrent_transmissions (``int``, *optional*):
            Set the maximum amount of concurrent transmissions (uploads & downloads).
            A value that is too high may result in network related issues.
            Defaults to 1.

        download_workers (``int``, *optional*):
            Set the number of concurrent chunk requests used to download a single file.
            Each worker downloads one 1 MiB chunk at a time, significantly reducing
            download time on high-latency connections.
            Defaults to 8.

        upload_workers (``int``, *optional*):
            Set the number of concurrent workers per media connection used to upload
            a single file (only for files bigger than 10 MiB, as smaller files are
            uploaded sequentially).
            Defaults to 4.

        max_message_cache_size (``int``, *optional*):
            Set the maximum size of the message cache.
            Defaults to 10000.

        max_business_user_connection_cache_size (``int``, *optional*):
            Set the maximum size of the message cache.
            Defaults to 10000.

        storage_engine (:obj:`~pyrogram.storage.Storage`, *optional*):
            Pass an instance of your own implementation of session storage engine.
            Useful when you want to store your session in databases like Mongo, Redis, etc.
            :doc:`Storage Engines </topics/storage-engines>`

        no_joined_notifications (``bool``, *optional*):
            Pass True to disable notification about the current user joining Telegram for other users that added them to contact list.
            Pass False to Notify people on Telegram who know my phone number that I signed up.
            Defaults to False

        client_platform (:obj:`~pyrogram.enums.ClientPlatform`, *optional*):
            The platform where this client is running.
            Defaults to 'other'
        
        link_preview_options (:obj:`~pyrogram.types.LinkPreviewOptions`, *optional*):
            Set the global link preview options for the client. By default, no link preview option is set.

        fetch_replies (``int``, *optional*):
            Set the number of replies to be fetched when parsing the :obj:`~pyrogram.types.Message` object. Defaults to 1.
            :doc:`More on Errors </api/errors/index>`

        rate_limits (``dict``, *optional*):
            Rate limits for different categories of API calls. Each category can have "rate" (calls/sec) and
            "burst" (max burst). Available categories: "message", "media", "query", "admin", "bulk", "account",
            "global". Example: ``{"message": {"rate": 20, "burst": 30}}``.
            Passing any value (even an empty dict) enables the client-side rate limiter with the given limits
            (or the built-in per-category defaults). The limiter is **disabled by
            default**; leave this ``None`` to send without client-side
            throttling, letting Telegram's server-side FloodWait handling (see *sleep_threshold*) manage the pace.

        auto_no_updates (``bool``, *optional*):
            Pass True to automatically wrap read-only and non-critical API calls with InvokeWithoutUpdates,
            reducing server-side update traffic and flood pressure.
            Defaults to True.

    """

    APP_VERSION = f"Pyrogram {__version__}"
    DEVICE_MODEL = f"{platform.python_implementation()} {platform.python_version()}"
    SYSTEM_VERSION = f"{platform.system()} {platform.release()}"

    LANG_PACK = ""
    LANG_CODE = "en"
    SYSTEM_LANG_CODE = "en"

    PARENT_DIR = Path(sys.argv[0]).parent

    INVITE_LINK_RE = re.compile(r"^(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog)/(?:joinchat/|\+))([\w-]+)$")
    TME_PUBLIC_LINK_RE = re.compile(r"^(?:https?://)?(?:www|([\w-]+)\.)?(?:t(?:elegram)?\.(?:org|me|dog))/?([\w-]+)?$")
    INVOICE_LINK_RE = re.compile(r"^(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog)/\$)([\w-]+)$")
    WORKERS = min(32, (os.cpu_count() or 0) + 4)  # os.cpu_count() can be None
    WORKDIR = PARENT_DIR

    # Interval of seconds in which the updates watchdog will kick in
    UPDATES_WATCHDOG_INTERVAL = 15 * 60

    MAX_CONCURRENT_TRANSMISSIONS = int(os.environ.get("DZGRAM_MAX_CONCURRENT_TRANSMISSIONS", 100))
    DOWNLOAD_WORKERS = 8
    UPLOAD_WORKERS = 4
    MAX_CACHE_SIZE = 10000

    MEDIA_SESSION_IDLE_TIMEOUT = int(os.environ.get("DZGRAM_MEDIA_SESSION_IDLE_TIMEOUT", 300))
    MEDIA_SESSION_REAP_INTERVAL = 60
    MAX_READ_AHEAD_CHUNKS = int(os.environ.get("DZGRAM_MAX_READ_AHEAD", 128))

    mimetypes = MimeTypes()
    mimetypes.readfp(StringIO(mime_types))

    def __init__(
        self,
        name: str,
        api_id: Union[int, str] = None,
        api_hash: str = None,
        app_version: str = APP_VERSION,
        device_model: str = DEVICE_MODEL,
        system_version: str = SYSTEM_VERSION,
        lang_pack: str = LANG_PACK,
        lang_code: str = LANG_CODE,
        system_lang_code: str = SYSTEM_LANG_CODE,
        ipv6: bool = False,
        proxy: dict = None,
        test_mode: bool = False,
        bot_token: str = None,
        session_string: str = None,
        in_memory: bool = None,
        phone_number: str = None,
        phone_code: str = None,
        password: str = None,
        workers: int = WORKERS,
        workdir: str = WORKDIR,
        plugins: dict = None,
        parse_mode: "enums.ParseMode" = enums.ParseMode.DEFAULT,
        no_updates: bool = None,
        skip_updates: bool = True,
        takeout: bool = None,
        sleep_threshold: int = int(os.environ.get("DZGRAM_SLEEP_THRESHOLD", 60)),
        hide_password: bool = False,
        max_concurrent_transmissions: int = MAX_CONCURRENT_TRANSMISSIONS,
        download_workers: int = DOWNLOAD_WORKERS,
        upload_workers: int = UPLOAD_WORKERS,
        max_message_cache_size: int = MAX_CACHE_SIZE,
        max_business_user_connection_cache_size: int = MAX_CACHE_SIZE,
        storage_engine: Storage = None,
        no_joined_notifications: bool = False,
        client_platform: enums.ClientPlatform = enums.ClientPlatform.OTHER,
        link_preview_options: "types.LinkPreviewOptions" = None,
        fetch_replies: int = 1,
        _un_docu_gnihts: list = [],
        rate_limits: Optional[dict] = None,
        auto_no_updates: bool = True
    ):
        super().__init__()

        self.name = name
        self.api_id = int(api_id) if api_id else None
        self.api_hash = api_hash
        self.app_version = app_version
        self.device_model = device_model
        self.system_version = system_version
        self.lang_pack = lang_pack.lower()
        self.lang_code = lang_code.lower()
        self.system_lang_code = system_lang_code.lower()
        self.ipv6 = ipv6
        self.proxy = proxy
        self.test_mode = test_mode
        self.bot_token = bot_token
        self.session_string = session_string
        self.in_memory = in_memory
        self.phone_number = phone_number
        self.phone_code = phone_code
        self.password = password
        self.workers = workers
        self.workdir = Path(workdir)
        self.plugins = plugins
        self.parse_mode = parse_mode
        self.no_updates = no_updates
        self.skip_updates = skip_updates
        self.takeout = takeout
        self.sleep_threshold = sleep_threshold
        self.hide_password = hide_password
        self.max_concurrent_transmissions = max_concurrent_transmissions
        self.download_workers = max(1, download_workers)
        self.upload_workers = max(1, upload_workers)
        self.max_message_cache_size = max_message_cache_size
        self.max_business_user_connection_cache_size = max_business_user_connection_cache_size
        self.no_joined_notifications = no_joined_notifications
        self.client_platform = client_platform
        self._un_docu_gnihts = _un_docu_gnihts
        self.link_preview_options = link_preview_options
        self.fetch_replies = fetch_replies
        # Per-category token bucket rate limiting (disabled when None,
        # preserving upstream Pyrogram behaviour) + auto InvokeWithoutUpdates
        # for read-only queries. Keep existing download TokenBucket intact.
        try:
            from pyrogram.methods.rate_limiter import RateLimiter
            self.rate_limiter = RateLimiter(rate_limits) if rate_limits is not None else None
        except Exception:
            self.rate_limiter = None
        self.auto_no_updates = auto_no_updates

        self.executor = ThreadPoolExecutor(self.workers, thread_name_prefix="Handler")

        if self.in_memory is None:
            # default to True when user session if true/false wasn't provided in init
            self.in_memory = bool(self.session_string)

        if isinstance(storage_engine, Storage):
            self.storage = storage_engine
        else:
            self.storage = SQLiteStorage(
                self.name,
                workdir=self.workdir,
                session_string=self.session_string,
                in_memory=self.in_memory,
            )

        self.dispatcher = Dispatcher(self)
        self.rnd_id = MsgId
        self.parser = Parser(self)
        self.session = None

        self.media_sessions = {}
        self.media_sessions_lock = asyncio.Lock()
        self.sessions = {}

        # Persistent pool of media sessions per DC used for uploads. Kept
        # alive between save_file() calls to avoid connection churn while
        # still allowing several parallel TCP connections per data center.
        self.upload_sessions = {}
        self.upload_sessions_lock = asyncio.Lock()

        # Pooled media sessions per DC used for parallel downloads/uploads.
        # Sessions are reused across transfers and reaped when idle.
        self.media_session_pools = {}
        self._media_sessions_locks = {}
        self._session_locks = {}
        self._session_creation_gate = asyncio.Semaphore(4)

        self.save_file_semaphore = asyncio.Semaphore(self.max_concurrent_transmissions)
        self.get_file_semaphore = asyncio.Semaphore(self.max_concurrent_transmissions)

        self.is_connected = None
        self.is_initialized = None

        self.takeout_id = None

        self.disconnect_handler = None

        # TODO: fix conditions here
        self.me: Optional[User] = None

        self.message_cache = Cache(self.max_message_cache_size)
        self.business_user_connection_cache = Cache(self.max_business_user_connection_cache_size)

        # Sometimes, for some reason, the server will stop sending updates and will only respond to pings.
        # This watchdog will invoke updates.GetState in order to wake up the server and enable it sending updates again
        # after some idle time has been detected.
        self.updates_watchdog_task = None
        self.updates_watchdog_event = asyncio.Event()
        self.last_update_time = datetime.now()
        self.listeners = {listener_type: [] for listener_type in pyrogram.enums.ListenerTypes}

        self.media_pool_reaper_task = None
        self.media_pool_reaper_event = asyncio.Event()

        self.loop = utils.get_event_loop()

    @property
    def read_ahead_slots(self) -> asyncio.Semaphore:
        return transfer_budget(self.MAX_READ_AHEAD_CHUNKS)

    def __enter__(self):
        return self.start()

    def __exit__(self, *args):
        try:
            self.stop()
        except ConnectionError:
            pass

    async def __aenter__(self):
        return await self.start()

    async def __aexit__(self, *args):
        try:
            await self.stop()
        except ConnectionError:
            pass

    async def updates_watchdog(self):
        while True:
            try:
                await asyncio.wait_for(self.updates_watchdog_event.wait(), self.UPDATES_WATCHDOG_INTERVAL)
            except asyncio.TimeoutError:
                pass
            else:
                break

            if self.updates_watchdog_event.is_set():
                break

            if datetime.now() - self.last_update_time > timedelta(seconds=self.UPDATES_WATCHDOG_INTERVAL):
                try:
                    await self.invoke(raw.functions.updates.GetState())
                except asyncio.CancelledError:
                    break
                except Exception:
                    # Watchdog probe must never kill the client.
                    # During stop()/terminate() the session may already be
                    # closing (e.g. OSError: 'NoneType' has no 'write'),
                    # so swallow it and let terminate() finish.
                    log.debug("updates_watchdog GetState failed, ignoring", exc_info=True)
                    # If shutdown was requested while the probe was in
                    # flight, exit promptly instead of looping.
                    if self.updates_watchdog_event.is_set():
                        break

    async def authorize(self) -> User:
        if self.bot_token:
            return await self.sign_in_bot(self.bot_token)

        print(f"Welcome to Pyrogram (version {__version__})")
        print(f"Pyrogram is free software and comes with ABSOLUTELY NO WARRANTY. Licensed\n"
              f"under the terms of the {__license__}.\n")

        while True:
            try:
                if not self.phone_number:
                    while True:
                        value = await ainput("Enter phone number or bot token: ")

                        if not value:
                            continue

                        confirm = (await ainput(f'Is "{value}" correct? (y/N): ')).lower()

                        if confirm == "y":
                            break

                    if ":" in value:
                        self.bot_token = value
                        return await self.sign_in_bot(value)
                    else:
                        self.phone_number = value

                sent_code = await self.send_code(self.phone_number)
            except BadRequest as e:
                print(e.MESSAGE)
                self.phone_number = None
                self.bot_token = None
            else:
                break

        if sent_code.type == enums.SentCodeType.SETUP_EMAIL_REQUIRED:
            print("Setup email required for authorization")

            while True:
                try:
                    while True:
                        email = await ainput("Enter setup email: ", loop=self.loop)

                        if not email:
                            continue

                        confirm = await ainput(f'Is "{email}" correct? (y/N): ', loop=self.loop)

                        if confirm.lower() == "y":
                            break

                    await self.invoke(
                        raw.functions.account.SendVerifyEmailCode(
                            purpose=raw.types.EmailVerifyPurposeLoginSetup(
                                phone_number=self.phone_number,
                                phone_code_hash=sent_code.phone_code_hash,
                            ),
                            email=email,
                        )
                    )

                    email_code = await ainput("Enter confirmation code received in setup email: ", loop=self.loop)

                    email_sent_code = await self.invoke(
                        raw.functions.account.VerifyEmail(
                            purpose=raw.types.EmailVerifyPurposeLoginSetup(
                                phone_number=self.phone_number,
                                phone_code_hash=sent_code.phone_code_hash,
                            ),
                            verification=raw.types.EmailVerificationCode(code=email_code),
                        )
                    )

                    if isinstance(email_sent_code, raw.types.account.EmailVerifiedLogin):
                        sent_code = types.SentCode._parse(email_sent_code.sent_code)
                except BadRequest as e:
                    print(e.MESSAGE)
                    self.phone_number = None
                    self.bot_token = None
                else:
                    break
        else:
            sent_code_descriptions = {
                enums.SentCodeType.APP: "Telegram app",
                enums.SentCodeType.CALL: "phone call",
                enums.SentCodeType.FLASH_CALL: "phone flash call",
                enums.SentCodeType.MISSED_CALL: "",
                enums.SentCodeType.SMS: "SMS",
                enums.SentCodeType.FRAGMENT_SMS: "Fragment SMS",
                enums.SentCodeType.FIREBASE_SMS: "SMS after Firebase attestation",
                enums.SentCodeType.EMAIL_CODE: "email",
                enums.SentCodeType.SETUP_EMAIL_REQUIRED: "add and verify email required",
            }

            print(f"The confirmation code has been sent via {sent_code_descriptions[sent_code.type]}")

        while True:
            if not self.phone_code:
                self.phone_code = await ainput("Enter confirmation code: ")
            try:
                signed_in = await self.sign_in(self.phone_number, sent_code.phone_code_hash, self.phone_code)
            except BadRequest as e:
                print(e.MESSAGE)
                self.phone_code = None
            except SessionPasswordNeeded as e:
                print(e.MESSAGE)

                while True:
                    print("Password hint: {}".format(await self.get_password_hint()))

                    if not self.password:
                        self.password = await ainput("Enter password (empty to recover): ", hide=self.hide_password)

                    try:
                        if not self.password:
                            confirm = await ainput("Confirm password recovery (y/n): ")

                            if confirm == "y":
                                email_pattern = await self.send_recovery_code()
                                print(f"The recovery code has been sent to {email_pattern}")

                                while True:
                                    recovery_code = await ainput("Enter recovery code: ")

                                    try:
                                        return await self.recover_password(recovery_code)
                                    except BadRequest as e:
                                        print(e.MESSAGE)
                                    except Exception as e:
                                        log.exception(e)
                                        raise
                            else:
                                self.password = None
                        else:
                            return await self.check_password(self.password)
                    except BadRequest as e:
                        print(e.MESSAGE)
                        self.password = None
            else:
                break

        if isinstance(signed_in, User):
            return signed_in

        while True:
            first_name = await ainput("Enter first name: ")
            last_name = await ainput("Enter last name (empty to skip): ")

            try:
                signed_up = await self.sign_up(
                    self.phone_number,
                    sent_code.phone_code_hash,
                    first_name,
                    last_name
                )
            except BadRequest as e:
                print(e.MESSAGE)
            else:
                break

        if isinstance(signed_in, TermsOfService):
            print("\n" + signed_in.text + "\n")
            await self.accept_terms_of_service(signed_in.id)

        return signed_up

    def set_parse_mode(self, parse_mode: Optional["enums.ParseMode"]):
        """Set the parse mode to be used globally by the client.

        When setting the parse mode with this method, all other methods having a *parse_mode* parameter will follow the
        global value by default.

        Parameters:
            parse_mode (:obj:`~pyrogram.enums.ParseMode`):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

        Example:
            .. code-block:: python

                from pyrogram import enums

                # Default combined mode: Markdown + HTML
                await app.send_message(chat_id="me", text="1. **markdown** and <i>html</i>")

                # Force Markdown-only, HTML is disabled
                app.set_parse_mode(enums.ParseMode.MARKDOWN)
                await app.send_message(chat_id="me", text="2. **markdown** and <i>html</i>")

                # Force HTML-only, Markdown is disabled
                app.set_parse_mode(enums.ParseMode.HTML)
                await app.send_message(chat_id="me", text="3. **markdown** and <i>html</i>")

                # Disable the parser completely
                app.set_parse_mode(enums.ParseMode.DISABLED)
                await app.send_message(chat_id="me", text="4. **markdown** and <i>html</i>")

                # Bring back the default combined mode
                app.set_parse_mode(enums.ParseMode.DEFAULT)
                await app.send_message(chat_id="me", text="5. **markdown** and <i>html</i>")
        """

        self.parse_mode = parse_mode

    async def fetch_peers(self, peers: list[Union[raw.types.User, raw.types.Chat, raw.types.Channel]]) -> bool:
        is_min = False
        parsed_peers = []

        for peer in peers:
            if getattr(peer, "min", False):
                is_min = True
                continue

            usernames = None
            phone_number = None

            if isinstance(peer, raw.types.User):
                peer_id = peer.id
                access_hash = peer.access_hash
                usernames = (
                    [peer.username.lower()] if peer.username
                    else [username.username.lower() for username in peer.usernames] if peer.usernames
                    else None
                )
                phone_number = peer.phone
                peer_type = "bot" if peer.bot else "user"
            elif isinstance(peer, (raw.types.Chat, raw.types.ChatForbidden)):
                peer_id = -peer.id
                access_hash = 0
                peer_type = "group"
            elif isinstance(peer, raw.types.Channel):
                peer_id = utils.get_channel_id(peer.id)
                access_hash = peer.access_hash
                usernames = (
                    [peer.username.lower()] if peer.username
                    else [username.username.lower() for username in peer.usernames] if peer.usernames
                    else None
                )
                peer_type = "channel" if peer.broadcast else "supergroup"
            elif isinstance(peer, raw.types.ChannelForbidden):
                peer_id = utils.get_channel_id(peer.id)
                access_hash = peer.access_hash
                peer_type = "channel" if peer.broadcast else "supergroup"
            else:
                continue

            parsed_peers.append((peer_id, access_hash, peer_type, usernames, phone_number))

        await self.storage.update_peers(parsed_peers)

        return is_min

    async def handle_updates(self, updates):
        self.last_update_time = datetime.now()

        if isinstance(updates, (raw.types.Updates, raw.types.UpdatesCombined)):
            is_min = any((
                await self.fetch_peers(updates.users),
                await self.fetch_peers(updates.chats),
            ))

            users = {u.id: u for u in updates.users}
            chats = {c.id: c for c in updates.chats}

            # Batch pts writes — one aiosqlite hand-off per peer
            # per batch instead of per update (only highest pts per channel matters)
            pending_states: dict[int, tuple] = {} if not self.skip_updates else None

            for update in updates.updates:
                channel_id = getattr(
                    getattr(
                        getattr(
                            update, "message", None
                        ), "peer_id", None
                    ), "channel_id", None
                ) or getattr(update, "channel_id", None)

                pts = getattr(update, "pts", None)
                pts_count = getattr(update, "pts_count", None)

                if pts and pending_states is not None:
                    key = utils.get_channel_id(channel_id) if channel_id else 0
                    known = pending_states.get(key)
                    if known is None or pts > known[1]:
                        pending_states[key] = (key, pts, None, updates.date, updates.seq)

                if isinstance(update, raw.types.UpdateChannelTooLong):
                    log.info(update)

                if isinstance(update, raw.types.UpdateNewChannelMessage) and is_min:
                    message = update.message

                    if not isinstance(message, raw.types.MessageEmpty):
                        try:
                            diff = await self.invoke(
                                raw.functions.updates.GetChannelDifference(
                                    channel=await self.resolve_peer(utils.get_channel_id(channel_id)),
                                    filter=raw.types.ChannelMessagesFilter(
                                        ranges=[raw.types.MessageRange(
                                            min_id=update.message.id,
                                            max_id=update.message.id
                                        )]
                                    ),
                                    pts=pts - pts_count,
                                    limit=pts,
                                    force=False
                                )
                            )
                        except (ChannelPrivate, PersistentTimestampOutdated, PersistentTimestampInvalid):
                            pass
                        else:
                            if not isinstance(diff, raw.types.updates.ChannelDifferenceEmpty):
                                users.update({u.id: u for u in diff.users})
                                chats.update({c.id: c for c in diff.chats})

                self.dispatcher.updates_queue.put_nowait((update, users, chats))

            if pending_states:
                for state in pending_states.values():
                    await self.storage.update_state(state)
        elif isinstance(updates, (raw.types.UpdateShortMessage, raw.types.UpdateShortChatMessage)):
            if not self.skip_updates:
                await self.storage.update_state(
                    (
                        0,
                        updates.pts,
                        None,
                        updates.date,
                        None
                    )
                )

            diff = await self.invoke(
                raw.functions.updates.GetDifference(
                    pts=updates.pts - updates.pts_count,
                    date=updates.date,
                    qts=-1
                )
            )

            if diff.new_messages:
                self.dispatcher.updates_queue.put_nowait((
                    raw.types.UpdateNewMessage(
                        message=diff.new_messages[0],
                        pts=updates.pts,
                        pts_count=updates.pts_count
                    ),
                    {u.id: u for u in diff.users},
                    {c.id: c for c in diff.chats}
                ))
            else:
                if diff.other_updates:  # The other_updates list can be empty
                    self.dispatcher.updates_queue.put_nowait((diff.other_updates[0], {}, {}))
        elif isinstance(updates, raw.types.UpdateShort):
            self.dispatcher.updates_queue.put_nowait((updates.update, {}, {}))
        elif isinstance(updates, raw.types.UpdatesTooLong):
            log.info(updates)

    async def recover_gaps(self) -> Tuple[int, int]:
        if self.skip_updates:
            log.info("Recover gaps disabled in client params. Skipping recovery")
            return (0, 0)

        states = await self.storage.update_state()

        if not states:
            log.info("No states found, skipping recovery")
            return (0, 0)

        message_updates_counter = 0
        other_updates_counter = 0

        log.info("Started gaps recovering...")

        for local_state in states:
            id, local_pts, local_qts, local_date, local_seq = local_state

            prev_pts = 0

            while True:
                try:
                    diff = await self.invoke(
                        raw.functions.updates.GetChannelDifference(
                            channel=await self.resolve_peer(id),
                            filter=raw.types.ChannelMessagesFilterEmpty(),
                            pts=local_pts,
                            limit=10000,
                            force=False
                        ) if id < 0 or id > MIN_MONOFORUM_CHANNEL_ID else
                        raw.functions.updates.GetDifference(
                            pts=local_pts,
                            date=local_date,
                            qts=0
                        )
                    )
                except (ChannelPrivate, ChannelInvalid, PersistentTimestampOutdated, PersistentTimestampInvalid):
                    break

                if isinstance(diff, raw.types.updates.DifferenceEmpty):
                    await self.storage.update_state(
                        (
                            id,
                            local_pts,
                            None,
                            diff.date,
                            diff.seq
                        )
                    )
                    break
                elif isinstance(diff, raw.types.updates.DifferenceTooLong):
                    await self.storage.update_state(
                        (
                            id,
                            diff.pts,
                            None,
                            local_date,
                            local_seq
                        )
                    )
                    continue
                elif isinstance(diff, raw.types.updates.Difference):
                    local_pts = diff.state.pts
                    local_date = diff.state.date
                    local_seq = diff.state.seq
                elif isinstance(diff, raw.types.updates.DifferenceSlice):
                    local_pts = diff.intermediate_state.pts
                    local_date = diff.intermediate_state.date
                    local_seq = diff.intermediate_state.seq

                    if prev_pts == local_pts:
                        break

                    prev_pts = local_pts
                elif isinstance(diff, raw.types.updates.ChannelDifferenceEmpty):
                    await self.storage.update_state(
                        (
                            id,
                            diff.pts,
                            None,
                            local_date,
                            local_seq
                        )
                    )
                    break
                elif isinstance(diff, raw.types.updates.ChannelDifferenceTooLong):
                    await self.storage.update_state(
                        (
                            id,
                            diff.dialog.pts,
                            None,
                            local_date,
                            local_seq
                        )
                    )
                    continue
                elif isinstance(diff, raw.types.updates.ChannelDifference):
                    local_pts = diff.pts

                users = {i.id: i for i in diff.users}
                chats = {i.id: i for i in diff.chats}

                for message in diff.new_messages:
                    message_updates_counter += 1
                    self.dispatcher.updates_queue.put_nowait(
                        (
                            raw.types.UpdateNewMessage(
                                message=message,
                                pts=local_pts,
                                pts_count=-1
                            ),
                            users,
                            chats
                        )
                    )

                for update in diff.other_updates:
                    other_updates_counter += 1
                    self.dispatcher.updates_queue.put_nowait(
                        (update, users, chats)
                    )

                if isinstance(diff, (raw.types.updates.Difference, raw.types.updates.ChannelDifference)):
                    break

            await self.storage.update_state(
                (
                    id,
                    local_pts,
                    None,
                    local_date,
                    local_seq
                )
            )

        log.info("Recovered %s messages and %s updates", message_updates_counter, other_updates_counter)
        return (message_updates_counter, other_updates_counter)

    async def load_session(self):
        await self.storage.open()

        session_empty = any([
            await self.storage.test_mode() is None,
            await self.storage.auth_key() is None,
            await self.storage.user_id() is None,
            await self.storage.is_bot() is None
        ])

        if session_empty:
            if not self.api_id or not self.api_hash:
                raise AttributeError(
                    "The API key is required for new authorizations. "
                    "More info: https://github.com/DownloaderZone/DzGram"
                )

            await self.storage.api_id(self.api_id)

            await self.storage.dc_id(2)
            await self.storage.date(0)

            await self.storage.test_mode(self.test_mode)
            await self.storage.auth_key(
                await Auth(
                    self, await self.storage.dc_id(),
                    await self.storage.test_mode()
                ).create()
            )
            await self.storage.user_id(None)
            await self.storage.is_bot(None)
        else:
            # Needed for migration from storage v2 to v3
            if not await self.storage.api_id():
                if self.api_id:
                    await self.storage.api_id(self.api_id)
                else:
                    while True:
                        try:
                            value = int(await ainput("Enter the api_id part of the API key: "))

                            if value <= 0:
                                print("Invalid value")
                                continue

                            confirm = (await ainput(f'Is "{value}" correct? (y/N): ')).lower()

                            if confirm == "y":
                                await self.storage.api_id(value)
                                break
                        except Exception as e:
                            print(e)

    def load_plugins(self):
        if self.plugins:
            plugins = self.plugins.copy()

            for option in ["include", "exclude"]:
                if plugins.get(option, []):
                    plugins[option] = [
                        (i.split()[0], i.split()[1:] or None)
                        for i in self.plugins[option]
                    ]
        else:
            return

        if plugins.get("enabled", True):
            root = plugins["root"]
            include = plugins.get("include", [])
            exclude = plugins.get("exclude", [])

            count = 0

            if not include:
                for path in sorted(Path(root.replace(".", "/")).rglob("*.py")):
                    module_path = '.'.join(path.parent.parts + (path.stem,))
                    module = import_module(module_path)

                    for name in vars(module).keys():
                        # noinspection PyBroadException
                        try:
                            for handler, group in getattr(module, name).handlers:
                                if isinstance(handler, Handler) and isinstance(group, int):
                                    self.add_handler(handler, group)

                                    log.info('[{}] [LOAD] {}("{}") in group {} from "{}"'.format(
                                        self.name, type(handler).__name__, name, group, module_path))

                                    count += 1
                        except Exception:
                            pass
            else:
                for path, handlers in include:
                    module_path = root + "." + path
                    warn_non_existent_functions = True

                    try:
                        module = import_module(module_path)
                    except ImportError:
                        log.warning('[%s] [LOAD] Ignoring non-existent module "%s"', self.name, module_path)
                        continue

                    if "__path__" in dir(module):
                        log.warning('[%s] [LOAD] Ignoring namespace "%s"', self.name, module_path)
                        continue

                    if handlers is None:
                        handlers = vars(module).keys()
                        warn_non_existent_functions = False

                    for name in handlers:
                        # noinspection PyBroadException
                        try:
                            for handler, group in getattr(module, name).handlers:
                                if isinstance(handler, Handler) and isinstance(group, int):
                                    self.add_handler(handler, group)

                                    log.info('[{}] [LOAD] {}("{}") in group {} from "{}"'.format(
                                        self.name, type(handler).__name__, name, group, module_path))

                                    count += 1
                        except Exception:
                            if warn_non_existent_functions:
                                log.warning('[{}] [LOAD] Ignoring non-existent function "{}" from "{}"'.format(
                                    self.name, name, module_path))

            if exclude:
                for path, handlers in exclude:
                    module_path = root + "." + path
                    warn_non_existent_functions = True

                    try:
                        module = import_module(module_path)
                    except ImportError:
                        log.warning('[%s] [UNLOAD] Ignoring non-existent module "%s"', self.name, module_path)
                        continue

                    if "__path__" in dir(module):
                        log.warning('[%s] [UNLOAD] Ignoring namespace "%s"', self.name, module_path)
                        continue

                    if handlers is None:
                        handlers = vars(module).keys()
                        warn_non_existent_functions = False

                    for name in handlers:
                        # noinspection PyBroadException
                        try:
                            for handler, group in getattr(module, name).handlers:
                                if isinstance(handler, Handler) and isinstance(group, int):
                                    self.remove_handler(handler, group)

                                    log.info('[{}] [UNLOAD] {}("{}") from group {} in "{}"'.format(
                                        self.name, type(handler).__name__, name, group, module_path))

                                    count -= 1
                        except Exception:
                            if warn_non_existent_functions:
                                log.warning('[{}] [UNLOAD] Ignoring non-existent function "{}" from "{}"'.format(
                                    self.name, name, module_path))

            if count > 0:
                log.info('[{}] Successfully loaded {} plugin{} from "{}"'.format(
                    self.name, count, "s" if count > 1 else "", root))
            else:
                log.warning('[%s] No plugin loaded from "%s"', self.name, root)

    async def media_pool_reaper(self):
        """Close pooled media sessions that have gone idle since their transfer ended."""
        while True:
            try:
                await asyncio.wait_for(
                    self.media_pool_reaper_event.wait(),
                    self.MEDIA_SESSION_REAP_INTERVAL
                )
            except asyncio.TimeoutError:
                pass
            else:
                break

            try:
                await self.reap_media_sessions()
            except Exception:
                log.exception("Media session reaper failed")

    async def reap_media_sessions(self, idle_timeout: Optional[int] = None) -> int:
        """Stop pooled media sessions unused for longer than *idle_timeout* seconds."""
        if idle_timeout is None:
            idle_timeout = self.MEDIA_SESSION_IDLE_TIMEOUT

        now = time.monotonic()
        reaped = 0

        for dc_id in list(self.media_session_pools):
            lock = self._media_sessions_locks.setdefault(dc_id, asyncio.Lock())

            async with lock:
                pool = self.media_session_pools.get(dc_id) or []
                keep = []

                for session in pool:
                    if session.results or now - session.last_used < idle_timeout:
                        keep.append(session)
                        continue

                    try:
                        await session.stop()
                    except Exception:
                        log.exception("Error stopping idle media session")

                    reaped += 1

                if keep:
                    self.media_session_pools[dc_id] = keep
                else:
                    self.media_session_pools.pop(dc_id, None)

        if reaped:
            log.info("Reaped %s idle media session(s)", reaped)

        return reaped

    async def get_session(
        self,
        dc_id: Optional[int] = None,
        is_media: bool = False,
        is_cdn: bool = False,
        temporary: bool = False,
    ) -> "Session":
        """Get an existing session or create a new one.

        This is the central factory for media/CDN sessions so concurrent
        transfers for the same DC share connections instead of racing
        ``auth.ExportAuthorization`` against each other.
        """
        if not dc_id:
            dc_id = await self.storage.dc_id()

        is_current_dc = await self.storage.dc_id() == dc_id

        if not temporary and is_current_dc and not is_media and not is_cdn:
            return self.session

        sessions = self.media_sessions if (is_media or is_cdn) else self.sessions

        if not temporary and sessions.get(dc_id):
            return sessions[dc_id]

        # Concurrent exports for one DC invalidate each other: AUTH_BYTES_INVALID.
        lock = self._session_locks.setdefault((dc_id, bool(is_media), bool(is_cdn)), asyncio.Lock())

        async with lock:
            if not temporary and sessions.get(dc_id):
                return sessions[dc_id]

            if is_cdn:
                async with self._session_creation_gate:
                    auth_key = await Auth(
                        self, dc_id, await self.storage.test_mode()
                    ).create()
            elif is_media and not is_current_dc:
                # Media sessions reuse the main DC auth key; fetch (or create)
                # the main session for that DC first, then share its key.
                main = await self.get_session(dc_id)
                auth_key = main.auth_key
            elif is_media:
                auth_key = await self.storage.auth_key()
            else:
                if not is_current_dc:
                    async with self._session_creation_gate:
                        auth_key = await Auth(
                            self, dc_id, await self.storage.test_mode()
                        ).create()
                else:
                    auth_key = await self.storage.auth_key()

            session = Session(
                self, dc_id, auth_key, await self.storage.test_mode(),
                is_media=is_media, is_cdn=is_cdn,
            )

            async with self._session_creation_gate:
                await session.start(max_attempts=Session.MAX_RETRIES)

            if not is_current_dc and (is_media or not is_media) and not is_cdn:
                # Export authorization for brand-new DCs (media sessions on a
                # foreign DC share the main DC auth key and still need it).
                for _ in range(3):
                    exported_auth = await self.invoke(
                        raw.functions.auth.ExportAuthorization(dc_id=dc_id)
                    )

                    try:
                        await session.invoke(
                            raw.functions.auth.ImportAuthorization(
                                id=exported_auth.id,
                                bytes=exported_auth.bytes
                            )
                        )
                    except AuthBytesInvalid:
                        await asyncio.sleep(1)
                        continue
                    else:
                        break
                else:
                    await session.stop()
                    raise AuthBytesInvalid

            if not temporary:
                sessions[dc_id] = session

            return session

    async def _make_media_session(self, dc_id: int, auth_key: bytes) -> "Session":
        session = Session(
            self, dc_id, auth_key, await self.storage.test_mode(), is_media=True,
        )
        await session.start(max_attempts=Session.MAX_RETRIES)
        return session

    async def _get_media_session_pool(self, dc_id: int, n: int) -> list:
        lock = self._media_sessions_locks.setdefault(dc_id, asyncio.Lock())
        async with lock:
            pool = []

            for session in self.media_session_pools.get(dc_id, []):
                if session.is_connected.is_set() or session.is_restarting:
                    pool.append(session)
                else:
                    try:
                        await session.stop()
                    except Exception:
                        log.exception("Error stopping dead media session")

            needed = n - len(pool)

            if needed > 0:
                media = await self.get_session(dc_id, is_media=True)

                while needed > 0:
                    chunk = min(needed, 3)
                    async with self._session_creation_gate:
                        pool.extend(await asyncio.gather(*(
                            self._make_media_session(dc_id, media.auth_key)
                            for _ in range(chunk)
                        )))
                    needed -= chunk

            self.media_session_pools[dc_id] = pool

            if self.media_pool_reaper_task is None or self.media_pool_reaper_task.done():
                try:
                    running = asyncio.get_running_loop()
                except RuntimeError:
                    running = None

                if running is not None:
                    self.media_pool_reaper_event.clear()
                    self.media_pool_reaper_task = running.create_task(self.media_pool_reaper())

            return list(pool)

    async def get_dc_option(
        self,
        dc_id: Optional[int] = None,
        is_media: bool = False,
        is_cdn: bool = False,
        ipv6: bool = False
    ) -> "raw.types.DcOption":
        config = await self.invoke(raw.functions.help.GetConfig())

        if dc_id is None:
            dc_id = config.this_dc

        options = [dc for dc in config.dc_options if dc.id == dc_id and dc.ipv6 == ipv6]

        if not options:
            raise ValueError(f"DC{dc_id} not found")

        if is_cdn:
            cdn_options = [dc for dc in options if dc.cdn]

            if cdn_options:
                return cdn_options[0]

            log.debug("No CDN datacenter found for DC%s, falling back to media DC", dc_id)
            is_media = True

        if is_media:
            media_options = [dc for dc in options if dc.media_only]

            if media_options:
                return media_options[0]

            log.debug("No media datacenter found for DC%s, falling back to prod DC", dc_id)

        prod_options = [dc for dc in options if not dc.media_only]

        if prod_options:
            return prod_options[0]

        raise ValueError("No suitable DC found")

    async def handle_download(self, packet):
        file_id, directory, file_name, in_memory, file_size, progress, progress_args = packet

        os.makedirs(directory, exist_ok=True) if not in_memory else None
        temp_file_path = os.path.abspath(re.sub("\\\\", "/", os.path.join(directory, file_name))) + ".temp"
        file = BytesIO() if in_memory else open(temp_file_path, "w+b")

        if not in_memory and file_size > 0:
            try:
                file.truncate(file_size)
            except OSError:
                pass

        try:
            async for chunk in self.get_file(
                file_id, file_size, 0, 0, progress, progress_args,
                _write_file=None if in_memory else file
            ):
                if in_memory:
                    file.write(chunk)
        except BaseException as e:
            if not in_memory:
                try:
                    file.close()
                finally:
                    try:
                        os.remove(temp_file_path)
                    except OSError:
                        pass

            if isinstance(e, asyncio.CancelledError):
                raise e

            if isinstance(e, pyrogram.StopTransmission):
                return None

            log.exception("Download failed")
            return None
        else:
            if in_memory:
                file.name = file_name
                return file
            else:
                file.close()
                file_path = os.path.splitext(temp_file_path)[0]
                shutil.move(temp_file_path, file_path)
                return file_path

    async def get_file(
        self,
        file_id: FileId,
        file_size: int = 0,
        limit: int = 0,
        offset: int = 0,
        progress: Optional[Callable] = None,
        progress_args: tuple = (),
        _write_file: object = None,
    ) -> AsyncGenerator[bytes, None]:
        async with self.get_file_semaphore:
            file_type = file_id.file_type

            if file_type == FileType.CHAT_PHOTO:
                if file_id.chat_id > 0:
                    peer = raw.types.InputPeerUser(
                        user_id=file_id.chat_id,
                        access_hash=file_id.chat_access_hash
                    )
                else:
                    if file_id.chat_access_hash == 0:
                        peer = raw.types.InputPeerChat(
                            chat_id=-file_id.chat_id
                        )
                    else:
                        peer = raw.types.InputPeerChannel(
                            channel_id=utils.get_channel_id(file_id.chat_id),
                            access_hash=file_id.chat_access_hash
                        )

                location = raw.types.InputPeerPhotoFileLocation(
                    peer=peer,
                    photo_id=file_id.media_id,
                    big=file_id.thumbnail_source == ThumbnailSource.CHAT_PHOTO_BIG
                )
            elif file_type == FileType.PHOTO:
                location = raw.types.InputPhotoFileLocation(
                    id=file_id.media_id,
                    access_hash=file_id.access_hash,
                    file_reference=file_id.file_reference,
                    thumb_size=file_id.thumbnail_size
                )
            else:
                location = raw.types.InputDocumentFileLocation(
                    id=file_id.media_id,
                    access_hash=file_id.access_hash,
                    file_reference=file_id.file_reference,
                    thumb_size=file_id.thumbnail_size
                )

            current = 0
            total = abs(limit) or (1 << 31) - 1
            chunk_size = 1024 * 1024
            offset_bytes = abs(offset) * chunk_size
            _last_progress_time = 0.0

            async def _report(sent: int) -> None:
                if not progress:
                    return

                func = functools.partial(
                    progress,
                    min(sent, file_size) if file_size else sent,
                    file_size,
                    *progress_args
                )

                try:
                    if inspect.iscoroutinefunction(progress):
                        await func()
                    else:
                        await self.loop.run_in_executor(self.executor, func)
                except pyrogram.StopTransmission:
                    raise
                except Exception as e:
                    log.warning(f"Download progress callback error: {e}")

            dc_id = file_id.dc_id

            try:
                _is_bot = self.me.is_bot if hasattr(self.me, 'is_bot') else False
                _is_premium = self.me.is_premium if hasattr(self.me, 'is_premium') else False

                if _is_bot:
                    dl_pool_size = 4
                    dl_workers_per_session = 4
                    dl_rate = int(os.environ.get("DZGRAM_BOT_DL_RATE", 30))
                    dl_burst = 15
                elif _is_premium:
                    dl_pool_size = 3
                    dl_workers_per_session = 6
                    dl_rate = int(os.environ.get("DZGRAM_PREMIUM_DL_RATE", 100))
                    dl_burst = 50
                else:
                    dl_pool_size = 3
                    dl_workers_per_session = 4
                    dl_rate = int(os.environ.get("DZGRAM_DL_RATE", 30))
                    dl_burst = 15

                total_chunks = math.ceil((file_size - offset_bytes) / chunk_size)
                pool_size = min(dl_pool_size, total_chunks)
                total_workers = min(dl_pool_size * dl_workers_per_session, total_chunks)
                needs_pool = min(total, total_chunks) > 1
                if needs_pool:
                    pool_task = asyncio.ensure_future(self._get_media_session_pool(dc_id, pool_size))
                    pool_task.add_done_callback(lambda t: t.cancelled() or t.exception())

                # Test hook: allow FakeMediaSession injection via media_sessions
                _fake = self.media_sessions.get(dc_id)
                if _fake is not None and not isinstance(_fake, Session):
                    session = _fake
                    use_fake = True
                else:
                    session = await self.get_session(dc_id, is_media=True)
                    use_fake = False
                    self.media_sessions[dc_id] = session

                r = await session.invoke(
                    raw.functions.upload.GetFile(
                        location=location,
                        offset=offset_bytes,
                        limit=chunk_size
                    ),
                    timeout=Session.MEDIA_WAIT_TIMEOUT,
                    sleep_threshold=30
                )

                if use_fake:
                    # Legacy single-session path for injected fakes (tests)
                    if file_size:
                        total = min(total, -(-file_size // chunk_size))
                    worker_count = min(self.download_workers, max(1, total))
                    pending = {}
                    next_chunk = 1
                    async def fetch(offset):
                        res = await session.invoke(
                            raw.functions.upload.GetFile(location=location, offset=offset, limit=chunk_size),
                            sleep_threshold=self.sleep_threshold
                        )
                        if isinstance(res, raw.types.upload.File):
                            return res.bytes
                        return b""
                    first = r.bytes
                    r = None
                    yield first
                    current += 1
                    first_len = len(first)
                    if _write_file is not None:
                        if _write_file.seekable():
                            try:
                                _write_file.seek(0)
                            except OSError:
                                pass
                        _write_file.write(first)
                    first = None
                    offset_bytes += chunk_size
                    await _report(offset_bytes)
                    if not first_len or first_len < chunk_size or current >= total:
                        return
                    base_offset = offset_bytes - chunk_size
                    while len(pending) < worker_count and next_chunk < total:
                        pending[next_chunk] = self.loop.create_task(fetch(base_offset + next_chunk * chunk_size))
                        next_chunk += 1
                    try:
                        if total <= 1:
                            return
                        while True:
                            if pending:
                                chunk = await pending.pop(min(pending))
                            else:
                                chunk = await fetch(offset_bytes)
                            while len(pending) < worker_count and next_chunk < total:
                                pending[next_chunk] = self.loop.create_task(fetch(base_offset + next_chunk * chunk_size))
                                next_chunk += 1
                            if _write_file is not None:
                                _write_file.write(chunk)
                            yield chunk
                            current += 1
                            offset_bytes += chunk_size
                            await _report(offset_bytes)
                            if len(chunk) < chunk_size or current >= total:
                                break
                    finally:
                        for task in pending.values():
                            task.cancel()
                        await __import__("asyncio").gather(*pending.values(), return_exceptions=True)
                    return
                if isinstance(r, raw.types.upload.File):
                    first_chunk = r.bytes
                    r = None
                    yield first_chunk
                    current += 1
                    offset_bytes += chunk_size
                    if _write_file is not None:
                        _write_file.seek(0)
                        _write_file.write(first_chunk)

                    first_len = len(first_chunk)
                    first_chunk = None

                    await _report(offset_bytes)

                    if not first_len or first_len < chunk_size or current >= total:
                        return

                    # Sequential fallback when file size is unknown
                    if file_size <= 0:
                        while current < total:
                            r = await session.invoke(
                                raw.functions.upload.GetFile(
                                    location=location,
                                    offset=offset_bytes,
                                    limit=chunk_size,
                                ),
                                timeout=Session.MEDIA_WAIT_TIMEOUT,
                                sleep_threshold=30,
                            )
                            chunk = r.bytes
                            if not chunk:
                                return
                            yield chunk
                            if _write_file is not None:
                                _write_file.write(chunk)
                            current += 1
                            offset_bytes += chunk_size

                            await _report(offset_bytes)

                            if len(chunk) < chunk_size or current >= total:
                                return
                        return

                    total_chunks = math.ceil((file_size - offset_bytes) / chunk_size)
                    pool_size = min(dl_pool_size, total_chunks)
                    total_workers = min(dl_pool_size * dl_workers_per_session, total_chunks)
                    if needs_pool:
                        pool = await pool_task
                    else:
                        pool = []
                    n_sessions = len(pool)

                    work = asyncio.Queue()
                    chunks_needed = min(
                        total - current,
                        math.ceil((file_size - offset_bytes) / chunk_size),
                    )
                    for i in range(chunks_needed):
                        work.put_nowait(offset_bytes + i * chunk_size)

                    _write_mode = _write_file is not None and file_size > 0
                    data_ready = asyncio.Event()
                    buffer_slots = ReadAhead(self.read_ahead_slots)
                    if not _write_mode:
                        received = {}
                    else:
                        _write_fd = _write_file.fileno()
                    _done_count = 0
                    _total_chunks = chunks_needed
                    _getfile_rate = TokenBucket(rate=dl_rate, burst=dl_burst)
                    _last_rate_adj = 0.0
                    _fast_window = 0

                    async def _worker(session):
                        nonlocal _done_count, _last_rate_adj, _fast_window
                        while True:
                            await buffer_slots.acquire()

                            try:
                                offset = work.get_nowait()
                            except asyncio.QueueEmpty:
                                buffer_slots.release()
                                return

                            try:
                                await _getfile_rate.acquire()
                                t0 = time.monotonic()
                                r = await session.invoke(
                                    raw.functions.upload.GetFile(
                                        location=location,
                                        offset=offset,
                                        limit=chunk_size,
                                    ),
                                    timeout=Session.MEDIA_WAIT_TIMEOUT,
                                    sleep_threshold=30,
                                )
                            except BaseException:
                                buffer_slots.release()
                                raise

                            chunk_data = r.bytes
                            r = None
                            t1 = time.monotonic()

                            if _write_mode:
                                write_at(_write_fd, chunk_data, offset)
                                buffer_slots.release()
                            else:
                                received[offset] = chunk_data

                            _done_count += 1
                            data_ready.set()

                            chunk_len = len(chunk_data)
                            chunk_data = None

                            if chunk_len < chunk_size:
                                return

                            elapsed = t1 - t0
                            now = t1
                            if elapsed > 2.0 and now - _last_rate_adj > 0.5:
                                _last_rate_adj = now
                                _fast_window = 0
                                _getfile_rate.rate = max(_getfile_rate.rate * 0.8, 3.0)
                            elif elapsed < 0.5:
                                _fast_window += 1
                                if _fast_window >= 5 and now - _last_rate_adj > 0.5:
                                    _last_rate_adj = now
                                    _getfile_rate.rate = min(_getfile_rate.rate + 2.0, dl_rate)
                                    _fast_window = 0
                            else:
                                _fast_window = 0

                    tasks = [
                        asyncio.ensure_future(_worker(pool[i % n_sessions]))
                        for i in range(total_workers)
                    ]

                    for t in tasks:
                        t.add_done_callback(lambda _: data_ready.set())

                    _reported_count = -1

                    try:
                        while current < total:
                            if _write_mode:
                                if _done_count >= _total_chunks:
                                    await _report(offset_bytes + _done_count * chunk_size)
                                    return
                                for t in tasks:
                                    if t.done() and not t.cancelled():
                                        exc = t.exception()
                                        if exc is not None:
                                            raise exc
                                if all(t.done() for t in tasks):
                                    return
                                try:
                                    await asyncio.wait_for(data_ready.wait(), 0.5)
                                except asyncio.TimeoutError:
                                    pass
                                data_ready.clear()

                                if _done_count != _reported_count:
                                    _reported_count = _done_count
                                    await _report(offset_bytes + _done_count * chunk_size)

                                yield b""
                            else:
                                while offset_bytes not in received:
                                    for t in tasks:
                                        if t.done() and not t.cancelled():
                                            exc = t.exception()
                                            if exc is not None:
                                                raise exc
                                    if all(t.done() for t in tasks):
                                        return
                                    await data_ready.wait()
                                    data_ready.clear()

                                chunk = received.pop(offset_bytes)
                                buffer_slots.release()
                                yield chunk
                                current += 1
                                offset_bytes += chunk_size

                                await _report(offset_bytes)

                                if len(chunk) < chunk_size or current >= total:
                                    return
                    finally:
                        for t in tasks:
                            if not t.done():
                                t.cancel()
                        buffer_slots.release_all()

                elif isinstance(r, raw.types.upload.FileCdnRedirect):
                    cdn_session = await self.get_session(
                        r.dc_id, is_media=True, is_cdn=True, temporary=True
                    )
                    _cdn_rate = TokenBucket(rate=dl_rate, burst=dl_burst)
                    _report_tasks = set()
                    _stop_requested = False

                    try:
                        while True:
                            await _cdn_rate.acquire()
                            r2 = await cdn_session.invoke(
                                raw.functions.upload.GetCdnFile(
                                    file_token=r.file_token,
                                    offset=offset_bytes,
                                    limit=chunk_size
                                ),
                                timeout=Session.MEDIA_WAIT_TIMEOUT
                            )

                            if isinstance(r2, raw.types.upload.CdnFileReuploadNeeded):
                                try:
                                    await session.invoke(
                                        raw.functions.upload.ReuploadCdnFile(
                                            file_token=r.file_token,
                                            request_token=r2.request_token
                                        )
                                    )
                                except VolumeLocNotFound:
                                    break
                                else:
                                    continue

                            chunk = r2.bytes

                            # https://core.telegram.org/cdn#decrypting-files
                            decrypted_chunk = await self.loop.run_in_executor(
                                self.crypto_executor,
                                aes.ctr256_decrypt,
                                chunk,
                                r.encryption_key,
                                bytearray(r.encryption_iv[:-4] + (offset_bytes // 16).to_bytes(4, "big"))
                            )

                            hashes = await session.invoke(
                                raw.functions.upload.GetCdnFileHashes(
                                    file_token=r.file_token,
                                    offset=offset_bytes
                                )
                            )

                            # https://core.telegram.org/cdn#verifying-files
                            def _check_all_hashes():
                                for i, h in enumerate(hashes):
                                    cdn_chunk = decrypted_chunk[h.limit * i: h.limit * (i + 1)]
                                    CDNFileHashMismatch.check(
                                        h.hash == sha256(cdn_chunk).digest(),
                                        "h.hash == sha256(cdn_chunk).digest()"
                                    )

                            await self.loop.run_in_executor(self.crypto_executor, _check_all_hashes)

                            if _stop_requested:
                                raise pyrogram.StopTransmission

                            yield decrypted_chunk

                            current += 1
                            offset_bytes += chunk_size

                            if progress:
                                _now = time.monotonic()
                                if _now - _last_progress_time >= 0.1:
                                    _last_progress_time = _now

                                    _sent = min(offset_bytes, file_size) if file_size != 0 else offset_bytes
                                    _total = file_size

                                    async def report(_sent=_sent, _total=_total):
                                        nonlocal _stop_requested
                                        try:
                                            if inspect.iscoroutinefunction(progress):
                                                await progress(_sent, _total, *progress_args)
                                            else:
                                                await self.loop.run_in_executor(
                                                    self.executor,
                                                    functools.partial(
                                                        progress, _sent, _total, *progress_args
                                                    ),
                                                )
                                        except pyrogram.StopTransmission:
                                            _stop_requested = True
                                        except Exception as e:
                                            log.warning(f"CDN download progress callback error: {e}")

                                    _t = asyncio.ensure_future(report())
                                    _report_tasks.add(_t)
                                    _t.add_done_callback(_report_tasks.discard)

                            if len(chunk) < chunk_size or current >= total:
                                break
                    finally:
                        for _t in list(_report_tasks):
                            if not _t.done():
                                _t.cancel()
                        await cdn_session.stop()
            except Exception:
                raise

    def guess_mime_type(self, filename: str) -> Optional[str]:
        return self.mimetypes.guess_type(filename)[0]

    def guess_extension(self, mime_type: str) -> Optional[str]:
        return self.mimetypes.guess_extension(mime_type)


class Cache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.store = {}

    def __getitem__(self, key):
        return self.store.get(key, None)

    def __setitem__(self, key, value):
        if key in self.store:
            del self.store[key]

        self.store[key] = value

        if len(self.store) > self.capacity:
            for _ in range(self.capacity // 2 + 1):
                del self.store[next(iter(self.store))]
