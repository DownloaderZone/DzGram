from typing import AsyncGenerator, Optional

import pyrogram
from pyrogram import raw, types, utils


class SearchPosts:
    async def search_posts(
        self: "pyrogram.Client",
        hashtag: Optional[str] = None,
        query: Optional[str] = None,
        limit: int = 0,
        allow_paid_stars: int = 0,
    ) -> AsyncGenerator["types.Message", None]:
        """Search public channel posts by hashtag or text."""
        if hashtag is None and query is None:
            raise ValueError("You must pass either hashtag or query")
        current = 0
        total = abs(limit) or (1 << 31) - 1
        page_size = min(100, total)
        offset_rate = 0
        offset_peer = raw.types.InputPeerEmpty()
        offset_id = 0
        while True:
            result = await self.invoke(raw.functions.channels.SearchPosts(
                hashtag=hashtag.lstrip("#") if hashtag is not None else None,
                query=query,
                offset_rate=offset_rate,
                offset_peer=offset_peer,
                offset_id=offset_id,
                limit=page_size,
                allow_paid_stars=allow_paid_stars,
            ), sleep_threshold=60)
            messages = await utils.parse_messages(self, result, replies=0)
            if not messages:
                return
            last = messages[-1]
            offset_rate = utils.datetime_to_timestamp(last.date)
            offset_peer = await self.resolve_peer(last.chat.id)
            offset_id = last.id
            for message in messages:
                yield message
                current += 1
                if current >= total:
                    return
