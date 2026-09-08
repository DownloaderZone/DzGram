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

import logging
import threading
import time

log = logging.getLogger(__name__)


class _MsgIdGenerator:
    _lock = threading.Lock()
    _last_msg_id = 0
    _base_wall = time.time()
    _base_mono = time.monotonic()
    time_offset = 0.0

    @classmethod
    def now(cls) -> float:
        return cls._base_wall + (time.monotonic() - cls._base_mono) + cls.time_offset

    @classmethod
    def sync(cls, server_msg_id: int, rejected: bool = False):
        with cls._lock:
            cls._base_wall = time.time()
            cls._base_mono = time.monotonic()
            cls.time_offset = (server_msg_id >> 32) - cls._base_wall

            if rejected:
                cls._last_msg_id = 0

        if abs(cls.time_offset) > 30:
            log.info("System clock is off, time offset set to %.1fs", cls.time_offset)

    def __call__(self) -> int:
        now = self.now()

        with _MsgIdGenerator._lock:
            msg_id = int(now * 2 ** 32) & ~3

            if msg_id <= _MsgIdGenerator._last_msg_id:
                msg_id = _MsgIdGenerator._last_msg_id + 4

            _MsgIdGenerator._last_msg_id = msg_id
            return msg_id


MsgId = _MsgIdGenerator()
