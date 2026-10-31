from typing import Iterable, List, Union

import pyrogram
from pyrogram import raw, types


class GetForumTopicsByID:
    async def get_forum_topics_by_id(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        topic_ids: Union[int, Iterable[int]],
    ) -> Union["types.ForumTopic", List["types.ForumTopic"]]:
        """Get one or more forum topics by identifier."""
        is_many = not isinstance(topic_ids, int)
        ids = list(topic_ids) if is_many else [topic_ids]
        result = await self.invoke(raw.functions.messages.GetForumTopicsByID(
            peer=await self.resolve_peer(chat_id),
            topics=ids,
        ))
        users = {item.id: item for item in result.users}
        chats = {item.id: item for item in result.chats}
        topics = types.List([
            types.ForumTopic._parse(self, item, users=users, chats=chats)
            for item in result.topics
        ])
        return topics if is_many else (topics[0] if topics else None)
