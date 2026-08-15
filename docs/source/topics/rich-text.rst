Rich Text
=========

DzGram supports Telegram's **rich messages** — fully formatted messages made of
*blocks* (headings, paragraphs, lists, tables, block quotes, media, ...) that
clients render natively. Unlike the classic entity-based text formatting
(:doc:`text-formatting`), rich messages are styled on the server side and can
carry structured content.

.. note::

    Rich messages are currently available to **bots** only.

-----

Sending Rich Text
-----------------

The simplest way to create a rich message is to pass the content as a string,
written either in HTML or in Markdown, exactly like regular formatted texts:

.. code-block:: python

    from pyrogram import enums

    await app.send_rich_message(
        chat_id,
        "<h1>Hello</h1><p>This is <b>bold</b> and <i>italic</i>.</p>",
        parse_mode=enums.ParseMode.HTML,
    )

    await app.send_rich_message(
        chat_id,
        "## Hello\n\nThis is **bold** and *italic*.",
        parse_mode=enums.ParseMode.MARKDOWN,
    )

See the `rich message formatting options`_ in the Bot API documentation for the
full list of supported tags.

The :meth:`~pyrogram.Client.send_message` and
:meth:`~pyrogram.Client.edit_message_text` methods also accept a *rich_text*
parameter (with its own *rich_text_parse_mode*, defaulting to Markdown):

.. code-block:: python

    await app.send_message(chat_id, rich_text="**Bold** text")

Composing Blocks
----------------

For programmatic access, build an :obj:`~pyrogram.types.InputRichMessage` out of
:obj:`~pyrogram.types.InputRichBlock` subclasses. Each block mirrors an HTML tag
or a rich message block type:

.. code-block:: python

    from pyrogram import types

    rich_message = types.InputRichMessage(
        blocks=[
            types.InputRichBlockSectionHeading(text="Welcome", size=1),
            types.InputRichBlockParagraph(text="Some text."),
            types.InputRichBlockList(
                items=[
                    types.InputRichBlockListItem(text="First"),
                    types.InputRichBlockListItem(text="Second"),
                ],
            ),
            types.InputRichBlockTable(
                title="Stats",
                rows=[
                    [
                        types.InputRichBlockTableCell(text="Name", header=True),
                        types.InputRichBlockTableCell(text="Value", header=True),
                    ],
                    [
                        types.InputRichBlockTableCell(text="Uptime"),
                        types.InputRichBlockTableCell(text="99.9%"),
                    ],
                ],
                bordered=True,
            ),
        ]
    )

Available blocks (see the API reference for the full parameter lists):

- :obj:`~pyrogram.types.InputRichBlockParagraph` — ``<p>``
- :obj:`~pyrogram.types.InputRichBlockSectionHeading` — ``<h1>``...``<h6>``
- :obj:`~pyrogram.types.InputRichBlockPreformatted` — ``<pre>``
- :obj:`~pyrogram.types.InputRichBlockFooter` — ``<footer>``
- :obj:`~pyrogram.types.InputRichBlockDivider` — ``<hr>``
- :obj:`~pyrogram.types.InputRichBlockMathematicalExpression` — LaTeX math
- :obj:`~pyrogram.types.InputRichBlockAnchor` — named anchor
- :obj:`~pyrogram.types.InputRichBlockList` / :obj:`~pyrogram.types.InputRichBlockListItem` — ``<ul>`` / ``<ol>``
- :obj:`~pyrogram.types.InputRichBlockBlockQuotation` / :obj:`~pyrogram.types.InputRichBlockPullQuotation` — quotes
- :obj:`~pyrogram.types.InputRichBlockCollage` / :obj:`~pyrogram.types.InputRichBlockSlideshow` — media groups
- :obj:`~pyrogram.types.InputRichBlockTable` / :obj:`~pyrogram.types.InputRichBlockTableCell` — ``<table>``
- :obj:`~pyrogram.types.InputRichBlockDetails` — collapsible ``<details>``
- :obj:`~pyrogram.types.InputRichBlockMap` — ``<tg-map>``
- :obj:`~pyrogram.types.InputRichBlockPhoto` / :obj:`~pyrogram.types.InputRichBlockVideo` / :obj:`~pyrogram.types.InputRichBlockAnimation` / :obj:`~pyrogram.types.InputRichBlockAudio` / :obj:`~pyrogram.types.InputRichBlockVoiceNote` — media
- :obj:`~pyrogram.types.InputRichBlockThinking` — "thinking" placeholder for drafts

Streaming Drafts
----------------

While generating content progressively (for example in AI bots), you can show
the user a live, animated preview of the partial rich message:

.. code-block:: python

    import asyncio

    draft_id = app.rnd_id()

    for i, word in enumerate(words):
        await app.send_rich_message_draft(
            chat_id,
            draft_id,
            types.InputRichMessage(html=" ".join(words[: i + 1])),
        )
        await asyncio.sleep(0.33)

    # Persist the final result
    await app.send_rich_message(chat_id, text)

The draft is ephemeral: clients drop it after a few seconds or as soon as a real
message arrives. Keep the *draft_id* constant for the whole generation and
throttle the calls (setTyping is rate-limited).

Receiving Rich Messages
-----------------------

When a rich message arrives, it is parsed into a
:obj:`~pyrogram.types.RichMessage` object, available as ``message.rich_message``.
It contains the list of :obj:`~pyrogram.types.RichBlock` and text is represented
by :obj:`~pyrogram.types.RichText` objects (or plain ``str``):

.. code-block:: python

    @app.on_message()
    async def on_message(client, message):
        if message.rich_message:
            for block in message.rich_message.blocks:
                print(block)

Inline Queries
--------------

Rich messages can also be used as the result of inline queries:

.. code-block:: python

    results = [
        types.InlineQueryResultArticle(
            title="Rich result",
            input_message_content=types.InputRichMessageContent(
                types.InputRichMessage(html="<h1>Hello!</h1>")
            )
        )
    ]

    await app.answer_inline_query(inline_query.id, results)

Ephemeral Messages
------------------

Ephemeral messages are visible only to a specific user and the bot in a group.
They support rich text too:

.. code-block:: python

    await app.send_ephemeral_message(
        chat_id,
        receiver_id=user_id,
        text="Hello!",
        rich_text="<b>Hello</b>!",
    )

    await app.delete_ephemeral_message(chat_id, user_id, message_id)

.. _rich message formatting options: https://core.telegram.org/bots/api#rich-message-formatting-options
