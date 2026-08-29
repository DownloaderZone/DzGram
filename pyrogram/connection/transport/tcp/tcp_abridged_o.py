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
import hashlib
import logging
import os
from typing import Optional

import pyrogram
from pyrogram.crypto import aes
from .tcp import TCP

log = logging.getLogger(__name__)


class TCPAbridgedO(TCP):
    RESERVED = (b"HEAD", b"POST", b"GET ", b"OPTI", b"\xdd\xdd\xdd\xdd", b"\xee\xee\xee\xee")

    def __init__(self, ipv6: bool, proxy: dict, loop: Optional[asyncio.AbstractEventLoop] = None):
        super().__init__(ipv6, proxy, loop)

        self.encrypt = None
        self.decrypt = None

    async def connect(self, address: tuple):
        await super().connect(address)

        while True:
            nonce = bytearray(os.urandom(64))

            if (
                nonce[0] != 0xEF
                and bytes(nonce[:4]) not in self.RESERVED
                and nonce[4:8] != b"\x00\x00\x00\x00"
            ):
                break

        reversed_tail = bytearray(nonce[55:7:-1])

        encrypt_key = hashlib.sha256(bytes(nonce[8:40])).digest()
        encrypt_iv = bytearray(nonce[40:56])
        decrypt_key = hashlib.sha256(bytes(reversed_tail[0:32])).digest()
        decrypt_iv = bytearray(reversed_tail[32:48])

        self.encrypt = (encrypt_key, encrypt_iv, bytearray(1))
        self.decrypt = (decrypt_key, decrypt_iv, bytearray(1))

        nonce[56:60] = b"\xef\xef\xef\xef"
        nonce[56:64] = aes.ctr256_encrypt(nonce, *self.encrypt)[56:64]

        await super().send(nonce)

    async def send(self, data: bytes, *args):
        length = len(data) // 4
        data = (bytes([length]) if length <= 126 else b"\x7f" + length.to_bytes(3, "little")) + data
        payload = await self.loop.run_in_executor(pyrogram.crypto_executor, aes.ctr256_encrypt, data, *self.encrypt)

        await super().send(payload)

    async def recv(self, length: int = 0) -> Optional[bytes]:
        length = await super().recv(1)

        if length is None:
            return None

        length = aes.ctr256_decrypt(length, *self.decrypt)

        if length == b"\x7f":
            length = await super().recv(3)

            if length is None:
                return None

            length = aes.ctr256_decrypt(length, *self.decrypt)

        data = await super().recv(int.from_bytes(length, "little") * 4)

        if data is None:
            return None

        return await self.loop.run_in_executor(pyrogram.crypto_executor, aes.ctr256_decrypt, data, *self.decrypt)
