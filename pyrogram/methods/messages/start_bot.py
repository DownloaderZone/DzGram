from typing import Optional, Union

import pyrogram
from pyrogram import raw, types


class StartBot:
    async def start_bot(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        param: str = "",
    ) -> Optional["types.Message"]:
        """Start a bot, optionally passing a deep-link parameter."""
        if not param:
            return await self.send_message(chat_id, "/start")
        peer = await self.resolve_peer(chat_id)
        result = await self.invoke(raw.functions.messages.StartBot(
            bot=peer,
            peer=peer,
            random_id=self.rnd_id(),
            start_param=param,
        ))
        users = {item.id: item for item in result.users}
        chats = {item.id: item for item in result.chats}
        for update in result.updates:
            if isinstance(update, (raw.types.UpdateNewMessage, raw.types.UpdateNewChannelMessage)):
                return await types.Message._parse(self, update.message, users, chats)
        return None
