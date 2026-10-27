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
import asyncio

import pyrogram
from pyrogram import raw

log = logging.getLogger(__name__)


class Start:
    async def start(
        self: "pyrogram.Client"
    ):
        """Start the client.

        This method connects the client to Telegram and, in case of new sessions, automatically manages the
        authorization process using an interactive prompt.

        Returns:
            :obj:`~pyrogram.Client`: The started client itself.

        Raises:
            ConnectionError: In case you try to start an already started client.

        Example:
            .. code-block:: python

                from pyrogram import Client

                app = Client("my_account")


                async def main():
                    await app.start()
                    ...  # Invoke API methods
                    await app.stop()


                app.run(main())
        """
        is_authorized = await self.connect()

        try:
            if not is_authorized:
                await self.authorize()

            if self.takeout and not await self.storage.is_bot():
                self.takeout_id = (await self.invoke(raw.functions.account.InitTakeoutSession())).id
                log.info("Takeout session %s initiated", self.takeout_id)

            await self.invoke(raw.functions.updates.GetState())
            self.me = await self.get_me()
            await self.initialize()
        except (Exception, KeyboardInterrupt, asyncio.CancelledError):
            await self.disconnect()
            raise
        else:
            return self
