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
import os


def transfer_budget(size: int) -> asyncio.Semaphore:
    """A semaphore capping the number of bytes read into memory at once."""
    return asyncio.Semaphore(max(1, size))


class ReadAhead:
    """A budget of slots for chunks being downloaded/uploaded at any given time.

    Each slot is borrowed before a chunk is requested and returned once the
    chunk has been written. The budget is shared between the producer (the
    generator calling get_file) and every parallel worker, so the total number
    of in-flight chunks never exceeds ``read_ahead_slots``.
    """

    def __init__(self, budget: asyncio.Semaphore):
        self._budget = budget
        self._held = 0

    async def acquire(self) -> None:
        await self._budget.acquire()
        self._held += 1

    def release(self) -> None:
        if self._held:
            self._held -= 1
            self._budget.release()

    def release_all(self) -> None:
        while self._held:
            self.release()


_pwrite = getattr(os, "pwrite", None)


def write_at(fd: int, data: bytes, offset: int) -> None:
    """Write *data* at *offset* without disturbing the file position.

    ``os.pwrite`` is POSIX-only. On Windows the seek and the write are two
    syscalls with no await between them, so concurrent download workers on the
    event loop cannot interleave.
    """
    if _pwrite is not None:
        n = _pwrite(fd, data, offset)

        if n != len(data):
            raise IOError(
                f"pwrite wrote {n} of {len(data)} bytes at offset {offset}"
            )
    else:
        os.lseek(fd, offset, os.SEEK_SET)
        os.write(fd, data)