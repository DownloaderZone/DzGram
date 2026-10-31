from typing import List, Optional, Union

import pyrogram
from pyrogram import raw


class SendReaction:
    async def send_reaction(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_id: int,
        emoji: Optional[Union[int, str, List[Union[int, str]]]] = None,
        big: bool = False,
        add_to_recent: bool = False,
    ) -> bool:
        """Send or retract a reaction on a message."""
        emojis = emoji if isinstance(emoji, list) else [emoji] if emoji else []
        reaction = [
            raw.types.ReactionCustomEmoji(document_id=item)
            if isinstance(item, int) else raw.types.ReactionEmoji(emoticon=item)
            for item in emojis
        ] or None
        await self.invoke(raw.functions.messages.SendReaction(
            peer=await self.resolve_peer(chat_id),
            msg_id=message_id,
            reaction=reaction,
            big=big,
            add_to_recent=add_to_recent,
        ))
        return True
