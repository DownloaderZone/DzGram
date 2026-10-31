from typing import Union

import pyrogram
from pyrogram import raw


class CheckUsername:
    async def check_username(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        username: str,
    ) -> bool:
        """Check whether a username is available for a chat or account."""
        peer = await self.resolve_peer(chat_id)
        if isinstance(peer, raw.types.InputPeerChannel):
            result = await self.invoke(raw.functions.channels.CheckUsername(
                channel=peer,
                username=username,
            ))
        else:
            result = await self.invoke(raw.functions.account.CheckUsername(
                username=username,
            ))
        return bool(result)
