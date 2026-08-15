Rich Text
=========

This example demonstrates DzGram's rich message support — messages with
block-based formatting such as headings, lists, tables, block quotes and more,
which are rendered natively by Telegram clients.

.. code-block:: python

    from pyrogram import Client, enums, types

    app = Client("my_bot", bot_token="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11")

    async def main():
        async with app:
            # 1. Send rich text written in HTML or Markdown
            await app.send_rich_message(
                "me",
                "<h1>DzGram</h1>"
                "<p>Rich messages support <b>bold</b>, <i>italic</i>, "
                "<blockquote>block quotes</blockquote> and more.</p>",
                parse_mode=enums.ParseMode.HTML,
            )

            # 2. Compose a rich message programmatically from blocks
            rich_message = types.InputRichMessage(
                blocks=[
                    types.InputRichBlockSectionHeading(text="Heading", size=1),
                    types.InputRichBlockParagraph(text="A paragraph of text."),
                    types.InputRichBlockList(
                        items=[
                            types.InputRichBlockListItem(text="First item"),
                            types.InputRichBlockListItem(text="Second item"),
                        ]
                    ),
                    types.InputRichBlockBlockQuotation(
                        blocks=[
                            types.InputRichBlockParagraph(text="Quoted text"),
                        ],
                        credit="Source",
                    ),
                    types.InputRichBlockPreformatted(
                        text="print('Hello')",
                        language="python",
                    ),
                ]
            )

            # 3. Stream a draft while content is being generated (e.g. AI bots)
            draft_id = app.rnd_id()
            await app.send_rich_message_draft("me", draft_id, rich_message)

            # 4. send_message and edit_message_text also accept rich_text
            await app.send_message(
                "me",
                rich_text="**Bold** and `code`",
                rich_text_parse_mode=enums.ParseMode.MARKDOWN,
            )

    app.run()

.. note::

    Rich messages are currently available to **bots** only. See the
    :doc:`../../topics/rich-text` topic for the full documentation of the
    feature.
