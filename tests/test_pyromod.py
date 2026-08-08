#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#  Copyright (C) 2022-present Mayuri-Chan <https://github.com/Mayuri-Chan>
#  Copyright (C) 2020 Cezar H. <https://github.com/usernein>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

import asyncio
import pytest

from pyrogram import Client, enums
from pyrogram.errors import ListenerTimeout
from pyrogram.types import Identifier, Listener


@pytest.fixture
def client():
    return Client("test", api_id=1, api_hash="test")


def test_identifier_matches():
    pattern = Identifier(chat_id=1, from_user_id=2)
    data = Identifier(chat_id=1, from_user_id=2, message_id=5)

    assert pattern.matches(data)
    assert not pattern.matches(Identifier(chat_id=3, from_user_id=2))


def test_identifier_lists():
    pattern = Identifier(chat_id=[1, 2])
    data = Identifier(chat_id=2, from_user_id=10)

    assert pattern.matches(data)
    assert not pattern.matches(Identifier(chat_id=3))


def test_identifier_count_populated():
    assert Identifier(chat_id=1, from_user_id=2).count_populated() == 2
    assert Identifier().count_populated() == 0


def test_client_has_listeners(client):
    assert client.listeners == {
        enums.ListenerTypes.MESSAGE: [],
        enums.ListenerTypes.CALLBACK_QUERY: [],
    }


def test_register_next_step_handler(client):
    def callback(client, message):
        pass

    client.register_next_step_handler(callback, chat_id=1)

    assert len(client.listeners[enums.ListenerTypes.MESSAGE]) == 1
    listener = client.listeners[enums.ListenerTypes.MESSAGE][0]
    assert listener.callback is callback
    assert listener.identifier.chat_id == 1


def test_get_listeners_matching(client):
    listener = Listener(
        listener_type=enums.ListenerTypes.MESSAGE,
        filters=None,
        unallowed_click_alert=True,
        identifier=Identifier(chat_id=1, from_user_id=2),
    )
    client.listeners[enums.ListenerTypes.MESSAGE].append(listener)

    assert client.get_listener_matching_with_data(
        Identifier(chat_id=1, from_user_id=2), enums.ListenerTypes.MESSAGE
    ) is listener

    assert client.get_listener_matching_with_identifier_pattern(
        Identifier(chat_id=1), enums.ListenerTypes.MESSAGE
    ) is listener

    assert client.get_many_listeners_matching_with_data(
        Identifier(chat_id=1, from_user_id=2), enums.ListenerTypes.MESSAGE
    ) == [listener]

    client.remove_listener(listener)
    assert client.listeners[enums.ListenerTypes.MESSAGE] == []


def test_listen_most_specific_wins(client):
    broad = Listener(
        listener_type=enums.ListenerTypes.MESSAGE,
        filters=None,
        unallowed_click_alert=True,
        identifier=Identifier(chat_id=1),
    )
    specific = Listener(
        listener_type=enums.ListenerTypes.MESSAGE,
        filters=None,
        unallowed_click_alert=True,
        identifier=Identifier(chat_id=1, from_user_id=2),
    )
    client.listeners[enums.ListenerTypes.MESSAGE].extend([broad, specific])

    listener = client.get_listener_matching_with_data(
        Identifier(chat_id=1, from_user_id=2), enums.ListenerTypes.MESSAGE
    )
    assert listener is specific


def test_listen_timeout(client):
    async def run():
        with pytest.raises(ListenerTimeout):
            await client.listen(chat_id=1, timeout=0.01)

    asyncio.get_event_loop().run_until_complete(run())


def test_listen_resolves_future(client):
    from pyrogram import StopPropagation, filters

    from pyrogram.handlers import MessageHandler
    from pyrogram.types import Chat, Message, User

    async def run():
        user = User(id=2, first_name="u", is_self=False, is_bot=False)
        chat = Chat(id=1, type="private")
        message = Message(id=10, outgoing=False, date=0, from_user=user, chat=chat)

        async def callback(client, message):
            pass

        handler = MessageHandler(callback)

        async def dispatch(m):
            try:
                await handler.resolve_future_or_callback(client, m)
            except StopPropagation:
                pass

        task = client.loop.create_task(client.listen(chat_id=1, user_id=2))
        await asyncio.sleep(0.05)
        assert not task.done()

        await dispatch(message)
        response = await asyncio.wait_for(task, 2)
        assert response is message
        assert not client.listeners[enums.ListenerTypes.MESSAGE]

    client.loop.run_until_complete(run())


def test_listen_filter_falls_back_to_handler(client):
    from pyrogram import StopPropagation, filters

    from pyrogram.handlers import MessageHandler
    from pyrogram.types import Chat, Message, User

    async def run():
        user = User(id=2, first_name="u", is_self=False, is_bot=False)
        chat = Chat(id=1, type="private")
        message = Message(id=10, outgoing=False, date=0, from_user=user, chat=chat)
        text_message = Message(id=11, outgoing=False, date=0, text="hello", from_user=user, chat=chat)

        received = []

        async def cb(client, message):
            received.append(message)

        handler = MessageHandler(cb)

        async def dispatch(m):
            try:
                await handler.resolve_future_or_callback(client, m)
            except StopPropagation:
                pass

        task = asyncio.get_event_loop().create_task(client.listen(chat_id=1, filters=filters.text))
        await asyncio.sleep(0.05)

        # text filter doesn't match -> not consumed, handler receives it
        await dispatch(message)
        assert not task.done()
        assert received == [message]

        # matching message resolves the listener
        await dispatch(text_message)
        response = await asyncio.wait_for(task, 2)
        assert response is text_message
        assert received == [message]

    client.loop.run_until_complete(run())


def test_wait_for_message(client):
    from pyrogram.handlers import MessageHandler
    from pyrogram.types import Chat, Message, User

    async def run():
        user = User(id=2, first_name="u", is_self=False, is_bot=False)
        chat = Chat(id=1, type="private")
        message = Message(id=10, outgoing=False, date=0, text="hello", from_user=user, chat=chat)

        task = client.loop.create_task(client.wait_for_message(1))
        await asyncio.sleep(0.05)

        conversation_handler = client.dispatcher.conversation_handler
        assert 1 in conversation_handler.waiters
        assert await conversation_handler.check(client, message)
        await conversation_handler.callback(client, message)

        response = await asyncio.wait_for(task, 2)
        assert response is message
        assert 1 not in conversation_handler.waiters

    client.loop.run_until_complete(run())