from typing import Union

import pyrogram
from pyrogram import raw, types, utils


class GetRichMessage:
    async def get_rich_message(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_id: int,
    ) -> "types.Message":
        """Fetch the complete contents of a truncated rich message."""
        result = await self.invoke(raw.functions.messages.GetRichMessage(
            peer=await self.resolve_peer(chat_id),
            id=message_id,
        ))
        messages = await utils.parse_messages(self, result, replies=0)
        return messages[0] if messages else None
