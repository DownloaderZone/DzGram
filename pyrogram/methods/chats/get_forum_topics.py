from typing import AsyncGenerator, Union

import pyrogram
from pyrogram import raw, types, utils


class GetForumTopics:
    async def get_forum_topics(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        limit: int = 0,
    ) -> AsyncGenerator["types.ForumTopic", None]:
        """Iterate over forum topics in a supergroup."""
        current = 0
        total = limit or (1 << 31) - 1
        page_size = min(100, total)
        offset_date = offset_id = offset_topic = 0
        while True:
            result = await self.invoke(raw.functions.messages.GetForumTopics(
                peer=await self.resolve_peer(chat_id),
                offset_date=offset_date,
                offset_id=offset_id,
                offset_topic=offset_topic,
                limit=page_size,
            ))
            users = {item.id: item for item in result.users}
            chats = {item.id: item for item in result.chats}
            messages = {
                item.id: await types.Message._parse(self, item, users, chats)
                for item in result.messages
                if not isinstance(item, raw.types.MessageEmpty)
            }
            topics = [types.ForumTopic._parse(self, item, messages, users, chats)
                      for item in result.topics]
            if not topics:
                return
            last = next((item.top_message for item in reversed(topics) if item.top_message), None)
            offset_id = last.id if last else 0
            offset_date = utils.datetime_to_timestamp(last.date) if last else 0
            offset_topic = topics[-1].id
            for topic in topics:
                yield topic
                current += 1
                if current >= total:
                    return
