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

from datetime import datetime
from typing import Dict, List, Literal, Optional, Union

import pyrogram
from pyrogram import raw, types, utils

from ..object import Object


def _get_ordered_list_label(num: int, list_type: Literal["a", "A", "i", "I", "1"]) -> str:
    if list_type in ("a", "A") and num > 0:
        result = ""
        temp_num = num

        while temp_num > 0:
            temp_num -= 1
            result = chr(ord("A" if list_type == "A" else "a") + temp_num % 26) + result
            temp_num //= 26

        return result + "."

    if list_type in ("i", "I") and num > 0 and num < 4000:
        val = [
            (1000, "M"),
            (900, "CM"),
            (500, "D"),
            (400, "CD"),
            (100, "C"),
            (90, "XC"),
            (50, "L"),
            (40, "XL"),
            (10, "X"),
            (9, "IX"),
            (5, "V"),
            (4, "IV"),
            (1, "I"),
        ]

        result = ""

        for value, numeral in val:
            count = int(num / value)
            result += numeral * count
            num -= value * count

        if list_type == "i":
            result = result.lower()

        return result + "."

    return f"{num}."


class RichBlock(Object):
    """This object represents a block in a rich formatted message.

    It can be one of:

    - :obj:`~pyrogram.types.RichBlockCaption`
    - :obj:`~pyrogram.types.RichBlockTableCell`
    - :obj:`~pyrogram.types.RichBlockListItem`
    - :obj:`~pyrogram.types.RichBlockParagraph`
    - :obj:`~pyrogram.types.RichBlockSectionHeading`
    - :obj:`~pyrogram.types.RichBlockPreformatted`
    - :obj:`~pyrogram.types.RichBlockFooter`
    - :obj:`~pyrogram.types.RichBlockDivider`
    - :obj:`~pyrogram.types.RichBlockMathematicalExpression`
    - :obj:`~pyrogram.types.RichBlockAnchor`
    - :obj:`~pyrogram.types.RichBlockList`
    - :obj:`~pyrogram.types.RichBlockBlockQuotation`
    - :obj:`~pyrogram.types.RichBlockPullQuotation`
    - :obj:`~pyrogram.types.RichBlockCollage`
    - :obj:`~pyrogram.types.RichBlockSlideshow`
    - :obj:`~pyrogram.types.RichBlockTable`
    - :obj:`~pyrogram.types.RichBlockDetails`
    - :obj:`~pyrogram.types.RichBlockMap`
    - :obj:`~pyrogram.types.RichBlockAnimation`
    - :obj:`~pyrogram.types.RichBlockAudio`
    - :obj:`~pyrogram.types.RichBlockPhoto`
    - :obj:`~pyrogram.types.RichBlockVideo`
    - :obj:`~pyrogram.types.RichBlockVoiceNote`
    - :obj:`~pyrogram.types.RichBlockThinking`
    - :obj:`~pyrogram.types.RichBlockTitle`
    - :obj:`~pyrogram.types.RichBlockSubtitle`
    - :obj:`~pyrogram.types.RichBlockAuthorDate`
    - :obj:`~pyrogram.types.RichBlockHeader`
    - :obj:`~pyrogram.types.RichBlockSubheader`
    - :obj:`~pyrogram.types.RichBlockKicker`
    - :obj:`~pyrogram.types.RichBlockRelatedArticles`
    - :obj:`~pyrogram.types.RichBlockCover`
    - :obj:`~pyrogram.types.RichBlockEmbedded`
    - :obj:`~pyrogram.types.RichBlockEmbeddedPost`
    - :obj:`~pyrogram.types.RichBlockChatLink`
    - :obj:`~pyrogram.types.RichBlockButtons`
    - :obj:`~pyrogram.types.RichBlockExpandableBlockQuotation`
    - :obj:`~pyrogram.types.RichBlockDocument`
    - :obj:`~pyrogram.types.RichBlockUnsupported`
    """

    def __init__(self):
        super().__init__()

    @staticmethod
    async def _parse(
        client: "pyrogram.Client",
        rich_block: "raw.base.PageBlock",
        photos: Dict[int, "raw.base.Photo"] = {},
        documents: Dict[int, "raw.base.Document"] = {},
        part: Optional[bool] = None,
        users: Dict[int, "raw.base.User"] = {},
        chats: Dict[int, "raw.base.Chat"] = {},
    ) -> "RichBlock":
        if isinstance(rich_block, raw.types.PageBlockParagraph):
            return RichBlockParagraph(
                text=await types.RichText._parse(client, rich_block.text),
            )
        if isinstance(rich_block, raw.types.PageBlockHeading1):
            return RichBlockSectionHeading(
                text=await types.RichText._parse(client, rich_block.text), size=1
            )
        if isinstance(rich_block, raw.types.PageBlockHeading2):
            return RichBlockSectionHeading(
                text=await types.RichText._parse(client, rich_block.text), size=2
            )
        if isinstance(rich_block, raw.types.PageBlockHeading3):
            return RichBlockSectionHeading(
                text=await types.RichText._parse(client, rich_block.text), size=3
            )
        if isinstance(rich_block, raw.types.PageBlockHeading4):
            return RichBlockSectionHeading(
                text=await types.RichText._parse(client, rich_block.text), size=4
            )
        if isinstance(rich_block, raw.types.PageBlockHeading5):
            return RichBlockSectionHeading(
                text=await types.RichText._parse(client, rich_block.text), size=5
            )
        if isinstance(rich_block, raw.types.PageBlockHeading6):
            return RichBlockSectionHeading(
                text=await types.RichText._parse(client, rich_block.text), size=6
            )
        if isinstance(rich_block, raw.types.PageBlockPreformatted):
            return RichBlockPreformatted(
                text=await types.RichText._parse(client, rich_block.text),
                language=rich_block.language,
            )
        if isinstance(rich_block, raw.types.PageBlockFooter):
            return RichBlockFooter(
                text=await types.RichText._parse(client, rich_block.text),
            )
        if isinstance(rich_block, raw.types.PageBlockDivider):
            return RichBlockDivider()
        if isinstance(rich_block, raw.types.PageBlockMath):
            return RichBlockMathematicalExpression(expression=rich_block.source)
        if isinstance(rich_block, raw.types.PageBlockAnchor):
            return RichBlockAnchor(name=rich_block.name)
        if isinstance(rich_block, raw.types.PageBlockList):
            return RichBlockList(
                items=types.List(
                    [await types.RichBlockListItem._parse(client, i) for i in rich_block.items]
                )
            )
        if isinstance(rich_block, raw.types.PageBlockOrderedList):
            return RichBlockList(
                items=types.List(
                    [await types.RichBlockListItem._parse(client, i) for i in rich_block.items]
                )
            )
        if isinstance(rich_block, raw.types.PageBlockBlockquoteBlocks):
            return RichBlockBlockQuotation(
                blocks=types.List(
                    [
                        await types.RichBlock._parse(
                            client, i, photos, documents, part, users, chats
                        )
                        for i in rich_block.blocks
                    ]
                ),
                credit=await types.RichText._parse(client, rich_block.caption),
            )
        if isinstance(rich_block, raw.types.PageBlockBlockquote):
            return RichBlockBlockQuotation(
                blocks=types.List(
                    [RichBlockParagraph(text=await types.RichText._parse(client, rich_block.text))]
                ),
                credit=await types.RichText._parse(client, rich_block.caption),
            )
        if isinstance(rich_block, raw.types.PageBlockPullquote):
            return RichBlockPullQuotation(
                text=await types.RichText._parse(client, rich_block.text),
                credit=await types.RichText._parse(client, rich_block.caption),
            )
        if isinstance(rich_block, raw.types.PageBlockCollage):
            return RichBlockCollage(
                blocks=types.List(
                    [
                        await types.RichBlock._parse(
                            client, i, photos, documents, part, users, chats
                        )
                        for i in rich_block.items
                    ]
                ),
                caption=await types.RichBlockCaption._parse(client, rich_block.caption),
            )
        if isinstance(rich_block, raw.types.PageBlockSlideshow):
            return RichBlockSlideshow(
                blocks=types.List(
                    [
                        await types.RichBlock._parse(
                            client, i, photos, documents, part, users, chats
                        )
                        for i in rich_block.items
                    ]
                ),
                caption=await types.RichBlockCaption._parse(client, rich_block.caption),
            )
        if isinstance(rich_block, raw.types.PageBlockTable):
            return await RichBlockTable._parse(client, rich_block)
        if isinstance(rich_block, raw.types.PageBlockDetails):
            return RichBlockDetails(
                summary=await types.RichText._parse(client, rich_block.title),
                blocks=types.List(
                    [
                        await types.RichBlock._parse(
                            client, i, photos, documents, part, users, chats
                        )
                        for i in rich_block.blocks
                    ]
                ),
                is_open=rich_block.open,
            )
        if isinstance(rich_block, raw.types.PageBlockMap):
            return RichBlockMap(
                location=types.Location._parse(rich_block.geo),
                zoom=rich_block.zoom,
                width=rich_block.w,
                height=rich_block.h,
                caption=await types.RichBlockCaption._parse(client, rich_block.caption),
            )
        if isinstance(rich_block, raw.types.PageBlockVideo):
            doc = documents.get(rich_block.video_id)
            if doc is None:
                return RichBlockUnsupported()
            attributes = {type(i): i for i in doc.attributes}

            file_name = getattr(
                attributes.get(raw.types.DocumentAttributeFilename, None), "file_name", None
            )

            if raw.types.DocumentAttributeAnimated in attributes:
                video_attributes = attributes.get(raw.types.DocumentAttributeVideo, None)

                return RichBlockAnimation(
                    animation=types.Animation._parse(client, doc, video_attributes, file_name),
                    has_spoiler=rich_block.spoiler,
                    caption=await types.RichBlockCaption._parse(client, rich_block.caption),
                )
            elif raw.types.DocumentAttributeVideo in attributes:
                video_attributes = attributes[raw.types.DocumentAttributeVideo]

                return RichBlockVideo(
                    video=types.Video._parse(client, doc, video_attributes, file_name),
                    has_spoiler=rich_block.spoiler,
                    caption=await types.RichBlockCaption._parse(client, rich_block.caption),
                )
            elif raw.types.DocumentAttributeAudio in attributes:
                audio_attributes = attributes[raw.types.DocumentAttributeAudio]

                if audio_attributes.voice:
                    return RichBlockVoiceNote(
                        voice_note=types.Voice._parse(client, doc, audio_attributes),
                        caption=await types.RichBlockCaption._parse(client, rich_block.caption),
                    )
                else:
                    return RichBlockAudio(
                        audio=types.Audio._parse(client, doc, audio_attributes, file_name),
                        caption=await types.RichBlockCaption._parse(client, rich_block.caption),
                    )
        if isinstance(rich_block, raw.types.PageBlockAudio):
            doc = documents.get(rich_block.audio_id)
            if doc is None:
                return RichBlockUnsupported()
            attributes = {type(i): i for i in doc.attributes}

            file_name = getattr(
                attributes.get(raw.types.DocumentAttributeFilename, None), "file_name", None
            )

            audio_attributes = attributes.get(raw.types.DocumentAttributeAudio, None)
            if audio_attributes is None:
                return RichBlockUnsupported()

            return RichBlockAudio(
                audio=types.Audio._parse(client, doc, audio_attributes, file_name),
                caption=await types.RichBlockCaption._parse(client, rich_block.caption),
            )
        if isinstance(rich_block, raw.types.PageBlockPhoto):
            return RichBlockPhoto(
                photo=types.Photo._parse(client, photos.get(rich_block.photo_id)),
                has_spoiler=rich_block.spoiler,
                caption=await types.RichBlockCaption._parse(client, rich_block.caption),
            )
        if isinstance(rich_block, raw.types.PageBlockThinking):
            return RichBlockThinking(text=await types.RichText._parse(client, rich_block.text))

        if isinstance(rich_block, raw.types.PageBlockTitle):
            return RichBlockTitle(text=await types.RichText._parse(client, rich_block.text))

        if isinstance(rich_block, raw.types.PageBlockSubtitle):
            return RichBlockSubtitle(text=await types.RichText._parse(client, rich_block.text))

        if isinstance(rich_block, raw.types.PageBlockAuthorDate):
            return RichBlockAuthorDate(
                author=await types.RichText._parse(client, rich_block.author),
                date=utils.timestamp_to_datetime(rich_block.published_date),
            )

        if isinstance(rich_block, raw.types.PageBlockHeader):
            return RichBlockHeader(text=await types.RichText._parse(client, rich_block.text))

        if isinstance(rich_block, raw.types.PageBlockSubheader):
            return RichBlockSubheader(text=await types.RichText._parse(client, rich_block.text))

        if isinstance(rich_block, raw.types.PageBlockKicker):
            return RichBlockKicker(text=await types.RichText._parse(client, rich_block.text))

        if isinstance(rich_block, raw.types.PageBlockRelatedArticles):
            return RichBlockRelatedArticles(
                header=await types.RichText._parse(client, rich_block.title),
                articles=types.List(
                    [
                        RichBlockRelatedArticle(
                            url=article.url,
                            title=article.title,
                            description=article.description,
                            photo=types.Photo._parse(client, photos.get(article.photo_id)),
                            author=article.author,
                            publish_date=utils.timestamp_to_datetime(article.published_date),
                        )
                        for article in rich_block.articles
                    ]
                ),
            )

        if isinstance(rich_block, raw.types.PageBlockCover):
            return RichBlockCover(
                cover=await RichBlock._parse(client, rich_block.cover, photos, documents, part, users, chats)
            )

        if isinstance(rich_block, raw.types.PageBlockEmbed):
            poster_photo = photos.get(rich_block.poster_photo_id)

            return RichBlockEmbedded(
                url=rich_block.url,
                html=rich_block.html,
                poster_photo=types.Photo._parse(client, poster_photo),
                width=rich_block.w,
                height=rich_block.h,
                caption=await types.RichBlockCaption._parse(client, rich_block.caption),
                is_full_width=rich_block.full_width,
                allow_scrolling=rich_block.allow_scrolling,
            )

        if isinstance(rich_block, raw.types.PageBlockEmbedPost):
            author_photo = photos.get(rich_block.author_photo_id)

            return RichBlockEmbeddedPost(
                url=rich_block.url,
                author=rich_block.author,
                author_photo=types.Photo._parse(client, author_photo),
                date=utils.timestamp_to_datetime(rich_block.date),
                blocks=types.List(
                    [
                        await types.RichBlock._parse(
                            client, block, photos, documents, part, users, chats
                        )
                        for block in rich_block.blocks
                    ]
                ),
                caption=await types.RichBlockCaption._parse(client, rich_block.caption),
            )

        if isinstance(rich_block, raw.types.PageBlockChannel):
            raw_chat = rich_block.channel

            if isinstance(raw_chat, raw.types.Channel):
                chat = types.Chat._parse_channel_chat(client, raw_chat)
            else:
                chat = types.Chat._parse_chat_chat(client, raw_chat)

            return RichBlockChatLink(
                title=chat.title,
                photo=chat.photo,
                accent_color_id=getattr(getattr(chat.accent_color, "color", None), "value", None),
                username=chat.username,
            )

        if isinstance(rich_block, raw.types.RichBlockButtons):
            return await RichBlockButtons._parse(client, rich_block)

        if isinstance(rich_block, raw.types.RichBlockExpandableBlockQuotation):
            return await RichBlockExpandableBlockQuotation._parse(client, rich_block)

        if isinstance(rich_block, raw.types.RichBlockDocument):
            return await RichBlockDocument._parse(client, rich_block)

        return RichBlockUnsupported()


class RichBlockUnsupported(RichBlock):
    """A rich block unsupported yet."""

    def __init__(
        self,
    ):
        super().__init__()


class RichBlockCaption(RichBlock):
    """Caption of a rich formatted block.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            Block caption.

        credit (:obj:`~pyrogram.types.RichText`, *optional*):
            Block credit which corresponds to the HTML tag <cite>.
    """

    def __init__(
        self,
        text: "types.RichText",
        credit: Optional["types.RichText"] = None,
    ):
        super().__init__()

        self.text = text
        self.credit = credit

    @staticmethod
    async def _parse(client, caption: "raw.base.PageCaption") -> Optional["RichBlockCaption"]:
        if caption is not None:
            return RichBlockCaption(
                text=await types.RichText._parse(client, caption.text),
                credit=await types.RichText._parse(client, caption.credit),
            )


class RichBlockTableCell(RichBlock):
    """Cell in a table.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`, *optional*):
            Text in the cell.
            If omitted, then the cell is invisible.

        is_header (``bool``, *optional*):
            True, if the cell is a header cell.

        colspan (``int``, *optional*):
            The number of columns the cell spans if it is bigger than 1.

        rowspan (``int``, *optional*):
            The number of rows the cell spans if it is bigger than 1.

        align (``str``, *optional*):
            Horizontal cell content alignment.
            Currently, must be one of "left", "center", or "right".

        valign (``str``, *optional*):
            Vertical cell content alignment.
            Currently, must be one of "top", "middle", or "bottom".
    """

    def __init__(
        self,
        text: Optional["types.RichText"] = None,
        is_header: Optional[bool] = None,
        colspan: Optional[int] = None,
        rowspan: Optional[int] = None,
        align: Optional[str] = None,
        valign: Optional[str] = None,
    ):
        super().__init__()

        self.text = text
        self.is_header = is_header
        self.colspan = colspan
        self.rowspan = rowspan
        self.align = align
        self.valign = valign

    @staticmethod
    async def _parse(client, table_cell: "raw.base.PageTableCell"):
        align = "left"
        if table_cell.align_center:
            align = "center"
        elif table_cell.align_right:
            align = "right"

        valign = "top"
        if table_cell.valign_middle:
            valign = "middle"
        elif table_cell.valign_bottom:
            valign = "bottom"

        return RichBlockTableCell(
            text=await types.RichText._parse(client, table_cell.text),
            is_header=table_cell.header,
            colspan=max(table_cell.colspan or 1, 1),
            rowspan=max(table_cell.rowspan or 1, 1),
            align=align,
            valign=valign,
        )


class RichBlockListItem(RichBlock):
    """An item of a list.

    Parameters:
        label (``str``):
            Label of the item.

        blocks (List of :obj:`~pyrogram.types.RichBlock`):
            The content of the item.

        has_checkbox (``bool``, *optional*):
            True, if the item has a checkbox.

        is_checked (``bool``, *optional*):
            True, if the item has a checked checkbox.

        value (``int``, *optional*):
            For ordered lists, the numeric value of the item label.

        type (``str``, *optional*):
            For ordered lists, the type of the item label.
            Must be one of "a" for lowercase letters, "A" for uppercase letters,
            "i" for lowercase Roman numerals, "I" for uppercase Roman numerals,
            or "1" for decimal numbers.
    """

    def __init__(
        self,
        label: str,
        blocks: List["types.RichBlock"],
        has_checkbox: Optional[bool] = None,
        is_checked: Optional[bool] = None,
        value: Optional[int] = None,
        type: Optional[str] = None,
    ):
        super().__init__()

        self.label = label
        self.blocks = blocks
        self.has_checkbox = has_checkbox
        self.is_checked = is_checked
        self.value = value
        self.type = type

    @staticmethod
    async def _parse(
        client, list_item: Union["raw.base.PageListItem", "raw.base.PageListOrderedItem"]
    ):
        if isinstance(list_item, raw.types.PageListItemBlocks):
            blocks = types.List(
                [await types.RichBlock._parse(client, block) for block in list_item.blocks]
            )
            label = "•"
            has_checkbox = list_item.checkbox
            is_checked = list_item.checked
            value = None
            item_type = None

        elif isinstance(list_item, raw.types.PageListItemText):
            blocks = types.List(
                [
                    types.RichBlockParagraph(
                        text=await types.RichText._parse(client, list_item.text)
                    )
                ]
            )
            label = "•"
            has_checkbox = list_item.checkbox
            is_checked = list_item.checked
            value = None
            item_type = None

        elif isinstance(list_item, raw.types.PageListOrderedItemBlocks):
            blocks = types.List(
                [await types.RichBlock._parse(client, block) for block in list_item.blocks]
            )
            has_checkbox = list_item.checkbox
            is_checked = list_item.checked
            value = list_item.value
            item_type = list_item.type or "1"

            if value is not None:
                label = _get_ordered_list_label(value, item_type)
            else:
                label = list_item.num

        elif isinstance(list_item, raw.types.PageListOrderedItemText):
            blocks = types.List(
                [
                    types.RichBlockParagraph(
                        text=await types.RichText._parse(client, list_item.text)
                    )
                ]
            )
            has_checkbox = list_item.checkbox
            is_checked = list_item.checked
            value = list_item.value
            item_type = list_item.type or "1"

            if value is not None:
                label = _get_ordered_list_label(value, item_type)
            else:
                label = list_item.num
        else:
            return None

        return RichBlockListItem(
            label=label,
            blocks=blocks,
            has_checkbox=has_checkbox,
            is_checked=is_checked,
            value=value,
            type=item_type,
        )


class RichBlockParagraph(RichBlock):
    """A text paragraph, corresponding to the HTML tag ``<p>``.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            Text of the block.
    """

    def __init__(
        self,
        text: "types.RichText",
    ):
        super().__init__()

        self.text = text


class RichBlockSectionHeading(RichBlock):
    """A section heading, corresponding to the HTML tags ``<h1>``, ``<h2>``, ``<h3>``, ``<h4>``, ``<h5>``, or ``<h6>``.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            Text of the block.

        size (``int``):
            Relative size of the text font, 1-6.
            1 is the largest, 6 is the smallest.
    """

    def __init__(
        self,
        text: "types.RichText",
        size: int,
    ):
        super().__init__()

        self.text = text
        self.size = size


class RichBlockPreformatted(RichBlock):
    """A preformatted text block, corresponding to the nested HTML tags ``<pre>`` and ``<code>``.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            Text of the block.

        language (``str``, *optional*):
            The programming language of the text.
    """

    def __init__(
        self,
        text: "types.RichText",
        language: Optional[str] = None,
    ):
        super().__init__()

        self.text = text
        self.language = language


class RichBlockFooter(RichBlock):
    """A footer, corresponding to the HTML tag ``<footer>``.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            Text of the block.
    """

    def __init__(self, text: "types.RichText"):
        super().__init__()

        self.text = text


class RichBlockDivider(RichBlock):
    """A divider, corresponding to the HTML tag ``<hr/>``."""

    def __init__(self):
        super().__init__()


class RichBlockMathematicalExpression(RichBlock):
    """A block with a mathematical expression in LaTeX format, corresponding to the custom HTML tag ``<tg-math-block>``.

    Parameters:
        expression (``str``):
            The mathematical expression in LaTeX format.
    """

    def __init__(self, expression: str):
        super().__init__()

        self.expression = expression


class RichBlockAnchor(RichBlock):
    """A block with an anchor, corresponding to the HTML tag ``<a>`` with the attribute ``name``.

    Parameters:
        name (``str``):
            The name of the anchor.
    """

    def __init__(self, name: str):
        super().__init__()

        self.name = name


class RichBlockList(RichBlock):
    """A list of blocks, corresponding to the HTML tag ``<ul>`` or ``<ol>`` with multiple nested tags ``<li>``.

    Parameters:
        items (List of :obj:`~pyrogram.types.RichBlockListItem`):
            Items of the list.
    """

    def __init__(self, items: List["types.RichBlockListItem"]):
        super().__init__()

        self.items = items


class RichBlockBlockQuotation(RichBlock):
    """A block quotation, corresponding to the HTML tag ``<blockquote>``.

    Parameters:
        blocks (List of :obj:`~pyrogram.types.RichBlock`):
            Content of the block.

        credit (:obj:`~pyrogram.types.RichText`, *optional*):
            Credit of the block.

        is_expandable (``bool``, *optional*):
            True, if the block quotation is expandable.
    """

    def __init__(
        self,
        blocks: List["types.RichBlock"],
        credit: Optional["types.RichText"] = None,
        is_expandable: Optional[bool] = None,
    ):
        super().__init__()

        self.blocks = blocks
        self.credit = credit
        self.is_expandable = is_expandable


class RichBlockPullQuotation(RichBlock):
    """A quotation with centered text, loosely corresponding to the HTML tag ``<aside>``.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            Text of the block.

        credit (:obj:`~pyrogram.types.RichText`, *optional*):
            Credit of the block.
    """

    def __init__(self, text: "types.RichText", credit: Optional["types.RichText"] = None):
        super().__init__()

        self.text = text
        self.credit = credit


class RichBlockCollage(RichBlock):
    """A collage, corresponding to the custom HTML tag ``<tg-collage>``.

    Parameters:
        blocks (List of :obj:`~pyrogram.types.RichBlock`):
            Elements of the collage.

        caption (:obj:`~pyrogram.types.RichBlockCaption`, *optional*):
            Caption of the block.
    """

    def __init__(
        self, blocks: List["types.RichBlock"], caption: Optional["types.RichBlockCaption"] = None
    ):
        super().__init__()

        self.blocks = blocks
        self.caption = caption


class RichBlockSlideshow(RichBlock):
    """A slideshow, corresponding to the custom HTML tag ``<tg-slideshow>``.

    Parameters:
        blocks (List of :obj:`~pyrogram.types.RichBlock`):
            Elements of the slideshow.

        caption (:obj:`~pyrogram.types.RichBlockCaption`, *optional*):
            Caption of the block.
    """

    def __init__(
        self, blocks: List["types.RichBlock"], caption: Optional["types.RichBlockCaption"] = None
    ):
        super().__init__()

        self.blocks = blocks
        self.caption = caption


class RichBlockTable(RichBlock):
    """A table, corresponding to the HTML tag ``<table>``.

    Parameters:
        cells (List of List of :obj:`~pyrogram.types.RichBlockTableCell`):
            Cells of the table.

        is_bordered (``bool``, *optional*):
            True, if the table has borders.

        is_striped (``bool``, *optional*):
            True, if the table is striped.

        is_compact (``bool``, *optional*):
            True, if the table is compact.

        caption (:obj:`~pyrogram.types.RichBlockCaption`, *optional*):
            Caption of the block.
    """

    def __init__(
        self,
        cells: List[List["types.RichBlockTableCell"]],
        is_bordered: Optional[bool] = None,
        is_striped: Optional[bool] = None,
        is_compact: Optional[bool] = None,
        caption: Optional["types.RichBlockCaption"] = None,
    ):
        super().__init__()

        self.cells = cells
        self.is_bordered = is_bordered
        self.is_striped = is_striped
        self.is_compact = is_compact
        self.caption = caption

    @staticmethod
    async def _parse(client, page_block: "raw.types.PageBlockTable"):
        cells = []

        if page_block.rows:
            for row in page_block.rows:
                row_cells = []
                if row.cells:
                    for table_cell in row.cells:
                        cell = await RichBlockTableCell._parse(client, table_cell)
                        row_cells.append(cell)

                if row_cells:
                    cells.append(row_cells)

        return RichBlockTable(
            cells=cells,
            is_bordered=page_block.bordered,
            is_striped=page_block.striped,
            is_compact=page_block.compact,
            caption=await types.RichText._parse(client, page_block.title),
        )


class RichBlockDetails(RichBlock):
    """An expandable block for details disclosure, corresponding to the HTML tag ``<details>``.

    Parameters:
        summary (:obj:`~pyrogram.types.RichText`):
            Always shown summary of the block.

        blocks (List of :obj:`~pyrogram.types.RichBlock`):
            Content of the block.

        is_open (``bool``, *optional*):
            True, if the content of the block is visible by default.
    """

    def __init__(
        self,
        summary: "types.RichText",
        blocks: List["types.RichBlock"],
        is_open: Optional[bool] = None,
    ):
        super().__init__()

        self.summary = summary
        self.blocks = blocks
        self.is_open = is_open


class RichBlockMap(RichBlock):
    """A block with a map, corresponding to the custom HTML tag ``<tg-map>``.

    Parameters:
        location (:obj:`~pyrogram.types.Location`):
            Location of the center of the map.

        zoom (``int``):
            Map zoom level, 13-20.

        width (``int``):
            Expected width of the map.

        height (``int``):
            Expected height of the map.

        caption (:obj:`~pyrogram.types.RichBlockCaption`, *optional*):
            Caption of the block.
    """

    def __init__(
        self,
        location: "types.Location",
        zoom: int,
        width: int,
        height: int,
        caption: Optional["types.RichBlockCaption"] = None,
    ):
        super().__init__()

        self.location = location
        self.zoom = zoom
        self.width = width
        self.height = height
        self.caption = caption


class RichBlockAnimation(RichBlock):
    """A block with an animation, corresponding to the HTML tag ``<video>``.

    Parameters:
        animation (:obj:`~pyrogram.types.Animation`):
            The animation.

        has_spoiler (``bool``, *optional*):
            True, if the media preview is covered by a spoiler animation.

        caption (:obj:`~pyrogram.types.RichBlockCaption`, *optional*):
            Caption of the block.
    """

    def __init__(
        self,
        animation: "types.Animation",
        has_spoiler: Optional[bool] = None,
        caption: Optional["types.RichBlockCaption"] = None,
    ):
        super().__init__()

        self.animation = animation
        self.has_spoiler = has_spoiler
        self.caption = caption


class RichBlockAudio(RichBlock):
    """A block with a music file, corresponding to the HTML tag ``<audio>``.

    Parameters:
        audio (:obj:`~pyrogram.types.Audio`):
            The audio.

        caption (:obj:`~pyrogram.types.RichBlockCaption`, *optional*):
            Caption of the block.
    """

    def __init__(self, audio: "types.Audio", caption: Optional["types.RichBlockCaption"] = None):
        super().__init__()

        self.audio = audio
        self.caption = caption


class RichBlockPhoto(RichBlock):
    """A block with a photo, corresponding to the HTML tag ``<photo>``.

    Parameters:
        photo (:obj:`~pyrogram.types.Photo`):
            The photo.

        has_spoiler (``bool``, *optional*):
            True, if the media preview is covered by a spoiler animation.

        caption (:obj:`~pyrogram.types.RichBlockCaption`, *optional*):
            Caption of the block.
    """

    def __init__(
        self,
        photo: "types.Photo",
        has_spoiler: Optional[bool] = None,
        caption: Optional["types.RichBlockCaption"] = None,
    ):
        super().__init__()

        self.photo = photo
        self.has_spoiler = has_spoiler
        self.caption = caption


class RichBlockVideo(RichBlock):
    """A block with a video, corresponding to the HTML tag ``<video>``.

    Parameters:
        video (:obj:`~pyrogram.types.Video`):
            The video.

        has_spoiler (``bool``, *optional*):
            True, if the media preview is covered by a spoiler animation.

        caption (:obj:`~pyrogram.types.RichBlockCaption`, *optional*):
            Caption of the block.
    """

    def __init__(
        self,
        video: "types.Video",
        has_spoiler: Optional[bool] = None,
        caption: Optional["types.RichBlockCaption"] = None,
    ):
        super().__init__()

        self.video = video
        self.has_spoiler = has_spoiler
        self.caption = caption


class RichBlockVoiceNote(RichBlock):
    """A block with a voice note, corresponding to the HTML tag ``<audio>``.

    Parameters:
        voice_note (:obj:`~pyrogram.types.Voice`):
            The voice note.

        caption (:obj:`~pyrogram.types.RichBlockCaption`, *optional*):
            Caption of the block.
    """

    def __init__(
        self, voice_note: "types.Voice", caption: Optional["types.RichBlockCaption"] = None
    ):
        super().__init__()

        self.voice_note = voice_note
        self.caption = caption


class RichBlockThinking(RichBlock):
    """A block with a "Thinking..." placeholder, corresponding to the custom HTML tag ``<tg-thinking>``.
    The block may be used only in :meth:`~pyrogram.Client.send_rich_message_draft`, therefore it can't be received in messages.
    See https://t.me/addemoji/AIActions for examples of custom emoji, which are recommended for usage in the block.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            Text of the block.
            See https://t.me/addemoji/AIActions for examples of custom emoji, which are recommended for usage in the block.
    """

    def __init__(
        self,
        text: "types.RichText",
    ):
        super().__init__()

        self.text = text


class RichBlockTitle(RichBlock):
    """A title, corresponding to the HTML tag ``<title>``.
    The title can be on the top of the page and may be followed by :obj:`~pyrogram.types.RichBlockSubtitle`,
    :obj:`~pyrogram.types.RichBlockAuthorDate` and :obj:`~pyrogram.types.RichBlockKicker` blocks.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            Text of the block.
    """

    def __init__(
        self,
        text: "types.RichText",
    ):
        super().__init__()

        self.text = text


class RichBlockSubtitle(RichBlock):
    """A subtitle, corresponding to the HTML tag ``<h2>``.
    The subtitle is below the title, may be followed by :obj:`~pyrogram.types.RichBlockAuthorDate` and
    :obj:`~pyrogram.types.RichBlockKicker` blocks.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            Text of the block.
    """

    def __init__(
        self,
        text: "types.RichText",
    ):
        super().__init__()

        self.text = text


class RichBlockAuthorDate(RichBlock):
    """The author and publishing date of a page, corresponding to the HTML tag ``<address>``.
    The block may be on the top of the page.

    Parameters:
        author (:obj:`~pyrogram.types.RichText`):
            Author of the page.

        date (:py:obj:`datetime.datetime`):
            Point in time when the page was published.
    """

    def __init__(
        self,
        author: "types.RichText",
        date: datetime,
    ):
        super().__init__()

        self.author = author
        self.date = date


class RichBlockHeader(RichBlock):
    """A header, corresponding to the HTML tag ``<header>``.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            Text of the block.
    """

    def __init__(
        self,
        text: "types.RichText",
    ):
        super().__init__()

        self.text = text


class RichBlockSubheader(RichBlock):
    """A subheader, corresponding to the HTML tag ``<h3>``.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            Text of the block.
    """

    def __init__(
        self,
        text: "types.RichText",
    ):
        super().__init__()

        self.text = text


class RichBlockKicker(RichBlock):
    """A kicker, corresponding to the HTML tag ``<kicker>``.
    The kicker is on the top of the page and may be followed by :obj:`~pyrogram.types.RichBlockTitle`,
    :obj:`~pyrogram.types.RichBlockSubtitle`, :obj:`~pyrogram.types.RichBlockAuthorDate` and
    :obj:`~pyrogram.types.RichBlockHeader` blocks.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            Text of the block.
    """

    def __init__(
        self,
        text: "types.RichText",
    ):
        super().__init__()

        self.text = text


class RichBlockRelatedArticles(RichBlock):
    """Related articles, corresponding to the HTML tag ``<related>``.

    Parameters:
        header (:obj:`~pyrogram.types.RichText`):
            Block header.

        articles (List of :obj:`~pyrogram.types.RichBlockRelatedArticle`):
            List of related articles.
    """

    def __init__(
        self,
        header: "types.RichText",
        articles: List["RichBlockRelatedArticle"],
    ):
        super().__init__()

        self.header = header
        self.articles = articles


class RichBlockRelatedArticle(RichBlock):
    """Contains information about a related article.

    Parameters:
        url (``str``):
            Related article URL.

        title (``str``, *optional*):
            Article title.

        description (``str``, *optional*):
            Article description.

        photo (:obj:`~pyrogram.types.Photo`, *optional*):
            Article photo.

        author (``str``, *optional*):
            Article author.

        publish_date (:py:obj:`datetime.datetime`, *optional*):
            Point in time when the article was published.
    """

    def __init__(
        self,
        url: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        photo: Optional["types.Photo"] = None,
        author: Optional[str] = None,
        publish_date: Optional[datetime] = None,
    ):
        super().__init__()

        self.url = url
        self.title = title
        self.description = description
        self.photo = photo
        self.author = author
        self.publish_date = publish_date


class RichBlockCover(RichBlock):
    """A page cover, corresponding to the HTML tag ``<cover>``.

    Parameters:
        cover (:obj:`~pyrogram.types.RichBlock`):
            The cover.
    """

    def __init__(
        self,
        cover: "types.RichBlock",
    ):
        super().__init__()

        self.cover = cover


class RichBlockEmbedded(RichBlock):
    """An embedded web page, corresponding to the HTML tag ``<embed>``.

    Parameters:
        url (``str``, *optional*):
            URL of the embedded page, if available.

        html (``str``, *optional*):
            HTML-markup of the embedded page.

        poster_photo (:obj:`~pyrogram.types.Photo`, *optional*):
            Poster photo, if available.

        width (``int``, *optional*):
            Block width, 0 if unknown.

        height (``int``, *optional*):
            Block height, 0 if unknown.

        caption (:obj:`~pyrogram.types.RichBlockCaption`, *optional*):
            Block caption.

        is_full_width (``bool``, *optional*):
            True, if the block must be full width.

        allow_scrolling (``bool``, *optional*):
            True, if scrolling needs to be allowed.
    """

    def __init__(
        self,
        url: Optional[str] = None,
        html: Optional[str] = None,
        poster_photo: Optional["types.Photo"] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        caption: Optional["RichBlockCaption"] = None,
        is_full_width: Optional[bool] = None,
        allow_scrolling: Optional[bool] = None,
    ):
        super().__init__()

        self.url = url
        self.html = html
        self.poster_photo = poster_photo
        self.width = width
        self.height = height
        self.caption = caption
        self.is_full_width = is_full_width
        self.allow_scrolling = allow_scrolling


class RichBlockEmbeddedPost(RichBlock):
    """An embedded post, corresponding to the HTML tag ``<embed-post>``.

    Parameters:
        url (``str``):
            URL of the embedded post.

        author (``str``):
            Post author.

        author_photo (:obj:`~pyrogram.types.Photo`, *optional*):
            Post author photo.

        date (:py:obj:`datetime.datetime`):
            Point in time when the post was created.

        blocks (List of :obj:`~pyrogram.types.RichBlock`):
            Post content.

        caption (:obj:`~pyrogram.types.RichBlockCaption`, *optional*):
            Post caption.
    """

    def __init__(
        self,
        url: str,
        author: str,
        date: datetime,
        blocks: List["types.RichBlock"],
        author_photo: Optional["types.Photo"] = None,
        caption: Optional["RichBlockCaption"] = None,
    ):
        super().__init__()

        self.url = url
        self.author = author
        self.author_photo = author_photo
        self.date = date
        self.blocks = blocks
        self.caption = caption


class RichBlockChatLink(RichBlock):
    """A link to a chat, corresponding to the HTML tag ``<chatlink>``.

    Parameters:
        title (``str``):
            Chat title.

        photo (:obj:`~pyrogram.types.ChatPhoto`, *optional*):
            Chat photo.

        accent_color_id (``int``, *optional*):
            Identifier of the accent color for chat title and background of chat photo.

        username (``str``, *optional*):
            Chat username by which all other information about the chat can be resolved.
    """

    def __init__(
        self,
        title: str,
        photo: Optional["types.ChatPhoto"] = None,
        accent_color_id: Optional[int] = None,
        username: Optional[str] = None,
    ):
        super().__init__()

        self.title = title
        self.photo = photo
        self.accent_color_id = accent_color_id
        self.username = username


class RichBlockButtons(RichBlock):
    """A block containing inline buttons for rich messages.

    Parameters:
        buttons (List of :obj:`~pyrogram.types.RichMessageButton`):
            List of buttons.

        alignment (``int``, *optional*):
            Alignment of buttons.
            0 = left, 1 = center, 2 = right.
    """

    def __init__(
        self,
        buttons: List["types.RichMessageButton"],
        alignment: Optional[int] = None,
    ):
        super().__init__()

        self.buttons = buttons
        self.alignment = alignment

    @staticmethod
    async def _parse(
        client: "pyrogram.Client",
        page_block: "raw.types.RichBlockButtons",
    ) -> "RichBlockButtons":
        buttons = types.List(
            [
                await types.RichMessageButton._parse(client, button)
                for button in page_block.buttons
            ]
        )

        return RichBlockButtons(
            buttons=buttons,
            alignment=page_block.alignment,
        )


class RichBlockExpandableBlockQuotation(RichBlock):
    """An expandable/collapsible block quotation.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            Content of the quotation.

        caption (:obj:`~pyrogram.types.RichText`):
            Caption, always shown as summary.

        collapsed_by_default (``bool``, *optional*):
            Whether collapsed by default.
    """

    def __init__(
        self,
        text: "types.RichText",
        caption: "types.RichText",
        collapsed_by_default: Optional[bool] = None,
    ):
        super().__init__()

        self.text = text
        self.caption = caption
        self.collapsed_by_default = collapsed_by_default

    @staticmethod
    async def _parse(
        client: "pyrogram.Client",
        page_block: "raw.types.RichBlockExpandableBlockQuotation",
    ) -> "RichBlockExpandableBlockQuotation":
        return RichBlockExpandableBlockQuotation(
            text=await types.RichText._parse(client, page_block.text),
            caption=await types.RichText._parse(client, page_block.caption),
            collapsed_by_default=page_block.collapsed_by_default,
        )


class RichBlockDocument(RichBlock):
    """A document block in rich messages.

    Parameters:
        document (:obj:`~pyrogram.types.Document`):
            The document.

        caption (:obj:`~pyrogram.types.RichText`, *optional*):
            Caption of the document.
    """

    def __init__(
        self,
        document: "types.Document",
        caption: Optional["types.RichText"] = None,
    ):
        super().__init__()

        self.document = document
        self.caption = caption

    @staticmethod
    async def _parse(
        client: "pyrogram.Client",
        page_block: "raw.types.RichBlockDocument",
    ) -> "RichBlockDocument":
        return RichBlockDocument(
            document=types.Document._parse(client, page_block.document),
            caption=await types.RichText._parse(client, page_block.caption),
        )

