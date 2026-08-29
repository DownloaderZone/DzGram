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
import ipaddress
import logging
import socket
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

try:
    import socks
except ImportError as e:
    e.msg = (
        "PySocks is missing and Pyrogram can't run without. "
        'Please install it using "pip3 install pysocks".'
    )

    raise e

from pyrogram import utils

log = logging.getLogger(__name__)


class TCP:
    TIMEOUT = 10

    def __init__(self, ipv6: bool, proxy: dict, loop: Optional[asyncio.AbstractEventLoop] = None):
        self.socket = None

        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None

        self.lock = asyncio.Lock()

        if isinstance(loop, asyncio.AbstractEventLoop):
            self.loop = loop
        else:
            self.loop = utils.get_event_loop()

        if proxy:
            hostname = proxy.get("hostname")

            try:
                ip_address = ipaddress.ip_address(hostname)
            except ValueError:
                self.socket = socks.socksocket(socket.AF_INET)
            else:
                if isinstance(ip_address, ipaddress.IPv6Address):
                    self.socket = socks.socksocket(socket.AF_INET6)
                else:
                    self.socket = socks.socksocket(socket.AF_INET)

            self.socket.set_proxy(
                proxy_type=getattr(socks, proxy.get("scheme").upper()),
                addr=hostname,
                port=proxy.get("port", None),
                username=proxy.get("username", None),
                password=proxy.get("password", None)
            )

            log.info("Using proxy %s", hostname)
        else:
            self.socket = socks.socksocket(
                socket.AF_INET6 if ipv6
                else socket.AF_INET
            )

        self.socket.settimeout(TCP.TIMEOUT)

    @staticmethod
    def _enable_keepalive(sock: socket.socket) -> None:
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

            if hasattr(socket, "TCP_KEEPIDLE"):
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 10)
            if hasattr(socket, "TCP_KEEPINTVL"):
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 5)
            if hasattr(socket, "TCP_KEEPCNT"):
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)
        except Exception as e:
            log.debug("Could not configure TCP Keep-Alive: %s %s", type(e).__name__, e)

    async def connect(self, address: tuple):
        # The socket used by the whole logic is blocking and thus it blocks when connecting.
        # Offload the task to a thread executor to avoid blocking the main event loop.
        with ThreadPoolExecutor(1) as executor:
            await self.loop.run_in_executor(executor, self.socket.connect, address)

        self._enable_keepalive(self.socket)

        self.reader, self.writer = await asyncio.open_connection(sock=self.socket)

    def close(self):
        try:
            self.writer.close()
        except AttributeError:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            finally:
                time.sleep(0.001)
                self.socket.close()

    async def send(self, data: bytes):
        async with self.lock:
            self.writer.write(data)
            await self.writer.drain()

    async def recv(self, length: int = 0):
        data = b""

        while len(data) < length:
            try:
                chunk = await asyncio.wait_for(
                    self.reader.read(length - len(data)),
                    TCP.TIMEOUT
                )
            except (OSError, asyncio.TimeoutError):
                return None
            else:
                if chunk:
                    data += chunk
                else:
                    return None

        return data
