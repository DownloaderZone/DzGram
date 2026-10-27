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

import logging

import pyrogram
from pyrogram import raw

log = logging.getLogger(__name__)


class GetPasswordHint:
    async def get_password_hint(
        self: "pyrogram.Client",
    ) -> str:
        """Get your Two-Step Verification password hint.

        .. include:: /_includes/usable-by/users.rst

        Returns:
            ``str``: On success, the password hint as string is returned.

        Raises:
            :obj:`~pyrogram.errors.RPCError`: In case of a Telegram RPC error.

        """
        return (await self.invoke(raw.functions.account.GetPassword())).hint
