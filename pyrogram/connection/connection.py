#  DzGram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#  Copyright (C) 2024-present Downloader Zone <https://github.com/DownloaderZone>
#
#  This file is part of DzGram, a fork of Pyrogram.
#
#  DzGram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  DzGram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with DzGram.  If not, see <http://www.gnu.org/licenses/>.

import asyncio
import logging
from typing import Optional

from .. import utils
from .transport import *
from ..session.internals import DataCenter

log = logging.getLogger(__name__)


def _close_quietly(protocol: Optional["TCP"]) -> None:
    """Close a transport without letting teardown errors escape."""
    if protocol is None:
        return

    try:
        protocol.close()
    except Exception as e:
        log.debug("Error closing transport: %s %s", type(e).__name__, e)


class Connection:
    MAX_RETRIES = 3

    MODES = {
        0: TCPFull,
        1: TCPAbridged,
        2: TCPIntermediate,
        3: TCPAbridgedO,
        4: TCPIntermediateO
    }

    def __init__(
        self,
        dc_id: int,
        test_mode: bool,
        ipv6: bool,
        proxy: dict,
        media: bool = False,
        mode: int = 1,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        server_address: Optional[str] = None,
        port: Optional[int] = None,
    ):
        self.dc_id = dc_id
        self.test_mode = test_mode
        self.ipv6 = ipv6
        self.proxy = proxy
        self.media = media
        default_address = DataCenter(dc_id, test_mode, ipv6, media) if not server_address or port is None else (server_address, port)
        self.address = (server_address or default_address[0], port if port is not None else default_address[1])
        self.mode = self.MODES.get(mode, TCPAbridged)

        self.protocol: Optional[TCP] = None
        self.connected = False

        if isinstance(loop, asyncio.AbstractEventLoop):
            self.loop = loop
        else:
            self.loop = utils.get_event_loop()

    async def connect(self):
        # A re-connect must never leave the previous transport referenced, so
        # drop it first: this object can own at most one live socket.
        self._drop_protocol()

        for i in range(Connection.MAX_RETRIES):
            # Build the transport locally and publish it only once it can
            # actually send. Publishing before connect() is what exposed a
            # writer that was still None to concurrent senders.
            protocol = self.mode(self.ipv6, self.proxy, loop=self.loop)

            try:
                log.info("Connecting...")
                await protocol.connect(self.address)
            except OSError as e:
                log.warning("Unable to connect due to network issues: %s", e)
                _close_quietly(protocol)
            except BaseException:
                # Cancellation and other failures must not leak the socket
                # that was being connected.
                _close_quietly(protocol)
                raise
            else:
                self.protocol = protocol
                self.connected = True

                log.info("Connected! %s DC%s%s - IPv%s - %s",
                         "Test" if self.test_mode else "Production",
                         self.dc_id,
                         " (media)" if self.media else "",
                         "6" if self.ipv6 else "4",
                         self.mode.__name__,
                )
                return

        log.warning("Connection failed! Trying again...")
        raise TimeoutError

    def _drop_protocol(self):
        protocol, self.protocol = self.protocol, None
        self.connected = False
        _close_quietly(protocol)

    def close(self):
        self._drop_protocol()
        log.info("Disconnected")

    async def send(self, data: bytes):
        protocol = self.protocol

        if protocol is None or not self.connected:
            # Never let a send reach a half-open transport: callers expect an
            # OSError they can retry (and reconnect) on.
            raise OSError("Connection is not established")

        try:
            await protocol.send(data)
        except (BrokenPipeError, ConnectionResetError) as e:
            raise OSError(e) from e
        except RuntimeError as e:
            # Transport is already closed; surface as OSError so the
            # caller can detect a closed/clogged connection.
            raise OSError(e) from e

    async def recv(self) -> Optional[bytes]:
        protocol = self.protocol

        if protocol is None:
            return None

        return await protocol.recv()
