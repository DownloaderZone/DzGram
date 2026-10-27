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

import pyrogram
from pyrogram import raw


class DeleteFolder:
    async def delete_folder(
        self: "pyrogram.Client",
        folder_id: int,
    ) -> bool:
        """Delete a dialog folder.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            folder_id (``int``):
                Identifier of the folder to delete.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.delete_folder(1)
        """
        await self.invoke(
            raw.functions.folders.DeleteFolder(
                folder_id=folder_id
            )
        )

        return True
