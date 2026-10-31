import re

import pyrogram
from pyrogram import raw


class ApplyGiftCode:
    async def apply_gift_code(self: "pyrogram.Client", link: str) -> bool:
        """Apply a Telegram gift code link."""
        match = re.match(
            r"^(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog)/(?:giftcode/|\+))([\w-]+)$",
            link,
        )
        if match:
            slug = match.group(1)
        elif isinstance(link, str):
            slug = link
        else:
            raise ValueError("Invalid gift code link")
        await self.invoke(raw.functions.payments.ApplyGiftCode(slug=slug))
        return True
