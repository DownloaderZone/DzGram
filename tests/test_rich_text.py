#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
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
from datetime import datetime, timezone

import pytest

from pyrogram import raw, types


class FakeClient:
    pass


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def plain(text: str) -> "raw.types.TextPlain":
    return raw.types.TextPlain(text=text)


def caption(text: str) -> "raw.types.PageCaption":
    return raw.types.PageCaption(text=plain(text), credit=raw.types.TextEmpty())


client = FakeClient()


def test_rich_text_plain():
    result = run(types.RichText._parse(client, plain("hello")))
    assert result == "hello"


def test_rich_text_concat():
    result = run(
        types.RichText._parse(
            client,
            raw.types.TextConcat(texts=[plain("a"), plain("b")]),
        )
    )
    assert result == ["a", "b"]


@pytest.mark.parametrize(
    "raw_text,expected_type",
    [
        (raw.types.TextBold, types.RichTextBold),
        (raw.types.TextItalic, types.RichTextItalic),
        (raw.types.TextUnderline, types.RichTextUnderline),
        (raw.types.TextStrike, types.RichTextStrikethrough),
        (raw.types.TextSpoiler, types.RichTextSpoiler),
        (raw.types.TextSubscript, types.RichTextSubscript),
        (raw.types.TextSuperscript, types.RichTextSuperscript),
        (raw.types.TextMarked, types.RichTextMarked),
        (raw.types.TextFixed, types.RichTextCode),
        (raw.types.TextMath, types.RichTextMathematicalExpression),
    ],
)
def test_rich_text_styles(raw_text, expected_type):
    if raw_text is raw.types.TextMath:
        result = run(types.RichText._parse(client, raw_text(source="x^2")))
        assert isinstance(result, expected_type)
        assert result.expression == "x^2"
        return
    result = run(types.RichText._parse(client, raw_text(text=plain("x"))))
    assert isinstance(result, expected_type)
    assert result.text == "x"


def test_rich_text_url():
    result = run(
        types.RichText._parse(
            client,
            raw.types.TextUrl(text=plain("x"), url="https://t.me", webpage_id=0),
        )
    )
    assert isinstance(result, types.RichTextUrl)
    assert result.url == "https://t.me"


def test_rich_text_anchor_link():
    result = run(
        types.RichText._parse(
            client,
            raw.types.TextUrl(text=plain("x"), url="#anchor", webpage_id=0),
        )
    )
    assert isinstance(result, types.RichTextAnchorLink)
    assert result.anchor_name == "anchor"


def test_rich_text_email():
    result = run(types.RichText._parse(client, raw.types.TextEmail(text=plain("x"), email="a@b.com")))
    assert isinstance(result, types.RichTextEmailAddress)
    assert result.email_address == "a@b.com"


def test_rich_text_phone():
    result = run(types.RichText._parse(client, raw.types.TextPhone(text=plain("x"), phone="+123")))
    assert isinstance(result, types.RichTextPhoneNumber)
    assert result.phone_number == "+123"


def test_rich_text_mention():
    result = run(types.RichText._parse(client, raw.types.TextMention(text=plain("@user"))))
    assert isinstance(result, types.RichTextMention)
    assert result.username == "user"


def test_rich_text_hashtag():
    result = run(types.RichText._parse(client, raw.types.TextHashtag(text=plain("#tag"))))
    assert isinstance(result, types.RichTextHashtag)
    assert result.hashtag == "tag"


def test_rich_text_cashtag():
    result = run(types.RichText._parse(client, raw.types.TextCashtag(text=plain("$USD"))))
    assert isinstance(result, types.RichTextCashtag)
    assert result.cashtag == "USD"


def test_rich_text_bot_command():
    result = run(types.RichText._parse(client, raw.types.TextBotCommand(text=plain("/start"))))
    assert isinstance(result, types.RichTextBotCommand)
    assert result.bot_command == "start"


def test_rich_text_custom_emoji():
    result = run(
        types.RichText._parse(
            client,
            raw.types.TextCustomEmoji(document_id=123, alt=":)" ),
        )
    )
    assert isinstance(result, types.RichTextCustomEmoji)
    assert result.custom_emoji_id == "123"
    assert result.alternative_text == ":)"


def test_rich_text_date():
    result = run(
        types.RichText._parse(
            client,
            raw.types.TextDate(text=plain("date"), date=1647531900, relative=False,
                               day_of_week=False, short_date=True, long_date=False,
                               short_time=False, long_time=True),
        )
    )
    assert isinstance(result, types.RichTextDateTime)
    assert result.date == datetime.fromtimestamp(1647531900, tz=timezone.utc)
    assert result.date_time_format == "dT"


def test_rich_text_anchor():
    result = run(types.RichText._parse(client, raw.types.TextAnchor(text=raw.types.TextEmpty(), name="top")))
    assert isinstance(result, types.RichTextAnchor)
    assert result.name == "top"


def test_rich_text_reference():
    result = run(types.RichText._parse(client, raw.types.TextAnchor(text=plain("ref"), name="ref1")))
    assert isinstance(result, types.RichTextReference)
    assert result.name == "ref1"


def test_rich_text_image():
    result = run(types.RichText._parse(client, raw.types.TextImage(document_id=1, w=100, h=50)))
    assert isinstance(result, types.RichTextImage)
    assert result.width == 100
    assert result.height == 50


def test_rich_text_diff():
    result = run(
        types.RichText._parse(
            client,
            raw.types.TextDiff(text=plain("new"), old_text=plain("old")),
        )
    )
    assert isinstance(result, types.RichTextDiff)
    assert result.text == "new"
    assert result.old_text == "old"


def test_rich_block_paragraph():
    result = run(types.RichBlock._parse(client, raw.types.PageBlockParagraph(text=plain("hello"))))
    assert isinstance(result, types.RichBlockParagraph)
    assert result.text == "hello"


@pytest.mark.parametrize(
    "raw_block,expected_type",
    [
        (raw.types.PageBlockTitle, types.RichBlockTitle),
        (raw.types.PageBlockSubtitle, types.RichBlockSubtitle),
        (raw.types.PageBlockHeader, types.RichBlockHeader),
        (raw.types.PageBlockSubheader, types.RichBlockSubheader),
        (raw.types.PageBlockKicker, types.RichBlockKicker),
    ],
)
def test_rich_block_headings(raw_block, expected_type):
    result = run(types.RichBlock._parse(client, raw_block(text=plain("heading"))))
    assert isinstance(result, expected_type)
    assert result.text == "heading"


def test_rich_block_author_date():
    result = run(
        types.RichBlock._parse(
            client,
            raw.types.PageBlockAuthorDate(author=plain("Dan"), published_date=1647531900),
        )
    )
    assert isinstance(result, types.RichBlockAuthorDate)
    assert result.author == "Dan"
    assert result.date == datetime.fromtimestamp(1647531900, tz=timezone.utc)


def test_rich_block_cover():
    result = run(
        types.RichBlock._parse(
            client,
            raw.types.PageBlockCover(cover=raw.types.PageBlockParagraph(text=plain("cov"))),
        )
    )
    assert isinstance(result, types.RichBlockCover)
    assert isinstance(result.cover, types.RichBlockParagraph)


def test_rich_block_related_articles():
    result = run(
        types.RichBlock._parse(
            client,
            raw.types.PageBlockRelatedArticles(
                title=plain("related"),
                articles=[
                    raw.types.PageRelatedArticle(
                        url="https://t.me", webpage_id=1, title="T", description="D",
                        photo_id=0, author="A", published_date=1647531900,
                    )
                ],
            ),
        )
    )
    assert isinstance(result, types.RichBlockRelatedArticles)
    assert result.header == "related"
    assert isinstance(result.articles[0], types.RichBlockRelatedArticle)
    assert result.articles[0].url == "https://t.me"
    assert result.articles[0].publish_date == datetime.fromtimestamp(1647531900, tz=timezone.utc)


def test_rich_block_embedded():
    result = run(
        types.RichBlock._parse(
            client,
            raw.types.PageBlockEmbed(
                caption=caption("cap"),
                url="https://t.me",
                html="<b>x</b>",
                w=640,
                h=480,
                full_width=True,
                allow_scrolling=True,
            ),
        )
    )
    assert isinstance(result, types.RichBlockEmbedded)
    assert result.url == "https://t.me"
    assert result.width == 640
    assert result.height == 480
    assert result.caption.text == "cap"
    assert result.is_full_width is True
    assert result.allow_scrolling is True


def test_rich_block_embedded_post():
    result = run(
        types.RichBlock._parse(
            client,
            raw.types.PageBlockEmbedPost(
                url="https://t.me/post",
                webpage_id=1,
                author_photo_id=0,
                author="Dan",
                date=1647531900,
                blocks=[raw.types.PageBlockParagraph(text=plain("hi"))],
                caption=caption("cap"),
            ),
        )
    )
    assert isinstance(result, types.RichBlockEmbeddedPost)
    assert result.author == "Dan"
    assert result.date == datetime.fromtimestamp(1647531900, tz=timezone.utc)
    assert isinstance(result.blocks[0], types.RichBlockParagraph)
    assert result.caption.text == "cap"


def test_rich_block_chat_link():
    channel = raw.types.Channel(
        id=12345,
        title="My Channel",
        photo=raw.types.ChatPhoto(photo_id=1, dc_id=2, stripped_thumb=b"xx"),
        date=0,
        username="mychan",
        usernames=[],
        restriction_reason=[],
        color=raw.types.PeerColor(color=4),
        access_hash=0,
    )
    result = run(types.RichBlock._parse(client, raw.types.PageBlockChannel(channel=channel)))
    assert isinstance(result, types.RichBlockChatLink)
    assert result.title == "My Channel"
    assert result.username == "mychan"
    assert result.accent_color_id == 4
    assert isinstance(result.photo, types.ChatPhoto)


def test_rich_block_table_cell():
    result = run(
        types.RichBlockTableCell._parse(
            client,
            raw.types.PageTableCell(
                text=plain("cell"),
                header=True,
                colspan=2,
                rowspan=3,
                align_center=True,
                valign_bottom=True,
            ),
        )
    )
    assert result.text == "cell"
    assert result.is_header is True
    assert result.colspan == 2
    assert result.rowspan == 3
    assert result.align == "center"
    assert result.valign == "bottom"


def test_rich_block_unsupported():
    result = run(types.RichBlock._parse(client, raw.types.PageBlockUnsupported()))
    assert isinstance(result, types.RichBlockUnsupported)


def test_rich_message():
    result = run(
        types.RichMessage._parse(
            client,
            raw.types.RichMessage(
                blocks=[
                    raw.types.PageBlockParagraph(text=plain("hello")),
                    raw.types.PageBlockHeading1(text=plain("title")),
                ],
                photos=[],
                documents=[],
                part=False,
                rtl=True,
            ),
        )
    )
    assert isinstance(result, types.RichMessage)
    assert result.is_rtl is True
    assert len(result.blocks) == 2
    assert isinstance(result.blocks[0], types.RichBlockParagraph)
    assert isinstance(result.blocks[1], types.RichBlockSectionHeading)