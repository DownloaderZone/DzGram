from typing import Optional, Union

import pyrogram
from pyrogram import raw, types


class CreateForumTopic:
    async def create_forum_topic(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        title: str,
        icon_color: Optional[int] = None,
        icon_emoji_id: Optional[int] = None,
        send_as: Optional[Union[int, str]] = None,
    ) -> "types.ForumTopicCreated":
        """Create a forum topic in a supergroup."""
        result = await self.invoke(raw.functions.messages.CreateForumTopic(
            peer=await self.resolve_peer(chat_id),
            title=title,
            random_id=self.rnd_id(),
            icon_color=icon_color,
            icon_emoji_id=icon_emoji_id,
            send_as=await self.resolve_peer(send_as) if send_as is not None else None,
        ))
        for update in result.updates:
            if isinstance(update, (raw.types.UpdateNewMessage, raw.types.UpdateNewChannelMessage)):
                return types.ForumTopicCreated._parse(update.message)
        return None
