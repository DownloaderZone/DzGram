from typing import List

import pyrogram
from pyrogram import raw


class GetBusinessChatLinks:
    async def get_business_chat_links(
        self: "pyrogram.Client",
    ) -> List["raw.types.BusinessChatLink"]:
        """Get all business chat links for the current account."""
        result = await self.invoke(raw.functions.account.GetBusinessChatLinks())
        return result.links
