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

from typing import Optional

from pyrogram.raw.core import Message, MsgContainer, TLObject
from pyrogram.raw.functions import Ping
from pyrogram.raw.types import MsgsAck, HttpWait
from .msg_id import MsgId, _MsgIdGenerator
from .seq_no import SeqNo

not_content_related = (Ping, HttpWait, MsgsAck, MsgContainer)


class MsgFactory:
    def __init__(self, msg_id_generator: Optional[_MsgIdGenerator] = None):
        self.seq_no = SeqNo()
        self.msg_id_gen = msg_id_generator or _MsgIdGenerator()

    def __call__(self, body: TLObject, length: Optional[int] = None) -> Message:
        return Message(
            body,
            self.msg_id_gen(),
            self.seq_no(not isinstance(body, not_content_related)),
            len(body) if length is None else length
        )
