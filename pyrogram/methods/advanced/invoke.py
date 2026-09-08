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

import logging
from typing import Optional, TypeVar

import pyrogram
from pyrogram import raw
from pyrogram.raw.core import TLObject
from pyrogram.session import Session
from pyrogram.methods.rate_limiter import RateLimiter

log = logging.getLogger(__name__)

ReturnType = TypeVar('ReturnType')

NO_UPDATES_QUERY_NAMES = frozenset({
    "account.CheckUsername",
    "account.GetPassword",
    "account.GetPrivacy",
    "account.GetWallPapers",
    "account.RegisterDevice",
    "account.UnregisterDevice",
    "channels.CheckUsername",
    "channels.GetAdminLog",
    "channels.GetChannels",
    "channels.GetGroupsForDiscussion",
    "channels.GetParticipants",
    "channels.ReadHistory",
    "channels.ReadMessageContents",
    "contacts.GetContacts",
    "contacts.GetTopPeers",
    "help.GetAppConfig",
    "help.GetConfig",
    "help.GetNearestDc",
    "help.GetTermsOfService",
    "langpack.GetLangPack",
    "langpack.GetLanguages",
    "messages.GetAllChats",
    "messages.GetAllDrafts",
    "messages.GetAllStickers",
    "messages.GetAttachMenuBots",
    "messages.GetAvailableEffects",
    "messages.GetBotCallbackAnswer",
    "messages.GetChatInviteImporters",
    "messages.GetChats",
    "messages.GetCommonChats",
    "messages.GetDefaultTagReactions",
    "messages.GetDialogs",
    "messages.GetEmojiKeywords",
    "messages.GetEmojiStickerGroups",
    "messages.GetEmojiStatusGroups",
    "messages.GetExtendedMedia",
    "messages.GetFavedStickers",
    "messages.GetFeaturedEmojiStickers",
    "messages.GetFeaturedStickers",
    "messages.GetForumTopics",
    "messages.GetFullChat",
    "messages.GetGameHighScores",
    "messages.GetHistory",
    "messages.GetMaskStickers",
    "messages.GetMessageReactionsList",
    "messages.GetMessages",
    "messages.GetMessagesViews",
    "messages.GetOldFeaturedStickers",
    "messages.GetPeerDialogs",
    "messages.GetPeerSettings",
    "messages.GetPinnedDialogs",
    "messages.GetPinnedSavedDialogs",
    "messages.GetPollResults",
    "messages.GetPollVotes",
    "messages.GetRecentReactions",
    "messages.GetRecentStickers",
    "messages.GetReplies",
    "messages.GetSavedDialogs",
    "messages.GetSavedGifs",
    "messages.GetSavedHistory",
    "messages.GetSavedReactionTags",
    "messages.GetScheduledHistory",
    "messages.GetScheduledMessages",
    "messages.GetSearchCounters",
    "messages.GetSplitRanges",
    "messages.GetStickerSet",
    "messages.GetStickers",
    "messages.GetSuggestedDialogFilters",
    "messages.GetTopReactions",
    "messages.GetUnreadMentions",
    "messages.GetUnreadReactions",
    "messages.GetWebPage",
    "messages.GetWebPagePreview",
    "messages.CheckHistoryImport",
    "messages.CheckQuickReplyShortcut",
    "messages.GetQuickReplies",
    "messages.GetQuickReplyMessages",
    "messages.GetMessagesFiltered",
    "messages.GetMessagesFilteredOrMin",
    "messages.GetMyStickers",
    "messages.GetCustomEmojiDocuments",
    "messages.GetDocumentInfo",
    "messages.Search",
    "messages.SearchCustomEmoji",
    "messages.SearchGlobal",
    "messages.SearchSentMedia",
    "messages.SearchStickerSets",
    "messages.SendScreenshotNotification",
    "messages.SetTyping",
    "stickers.CheckShortName",
    "stickers.SuggestShortName",
    "updates.GetChannelDifference",
    "updates.GetDifference",
    "updates.GetState",
    "upload.GetFile",
    "upload.GetWebFile",
    "upload.ReuploadCdnFile",
    "upload.SaveBigFilePart",
    "upload.SaveFilePart",
    "users.GetFullUser",
    "users.GetUsers",
    "premium.GetMyBoosts",
    "premium.GetBoostsList",
    "premium.GetUserBoosts",
})


INNER_QUERY_ATTR = "query"

INVOKE_WRAPPERS = (
    raw.functions.InvokeWithoutUpdates,
    raw.functions.InvokeWithTakeout,
    raw.functions.InvokeWithBusinessConnection,
)


class Invoke:
    @staticmethod
    def _unwrap(query: TLObject) -> TLObject:
        while isinstance(query, INVOKE_WRAPPERS):
            query = getattr(query, INNER_QUERY_ATTR, query)
        return query

    def _classify_query(self, query: TLObject) -> str:
        inner = self._unwrap(query)

        name = inner.QUALNAME if hasattr(inner, "QUALNAME") else type(inner).__name__
        short = name.split(".")[-1] if "." in name else name

        if any(x in name for x in ("Send", "Upload", "Edit", "Forward", "Save")):
            if any(x in name for x in ("Media", "Photo", "Video", "Audio", "Document", "Animation", "Voice", "Sticker", "Round")):
                return RateLimiter.CATEGORY_MEDIA
            return RateLimiter.CATEGORY_MESSAGE

        if any(x in name for x in ("Delete", "Ban", "Kick", "Unban", "Promote", "EditAdmin", "EditBanned", "Toggle", "Set", "Pin", "Report", "Block")):
            return RateLimiter.CATEGORY_ADMIN

        if any(x in name for x in ("GetDifference", "GetState", "Ping", "HttpWait")):
            return RateLimiter.CATEGORY_BULK

        if short.startswith("Get") or short.startswith("Search") or short.startswith("Check"):
            return RateLimiter.CATEGORY_QUERY

        return RateLimiter.CATEGORY_QUERY

    def _auto_needs_updates(self, query: TLObject) -> bool:
        inner = self._unwrap(query)

        fqn = inner.QUALNAME if hasattr(inner, "QUALNAME") else None
        if fqn and fqn.startswith("functions."):
            fqn = fqn[len("functions."):]
        if fqn and fqn in NO_UPDATES_QUERY_NAMES:
            return False

        name = type(inner).__name__ if hasattr(type(inner), "__name__") else ""
        if name.startswith("Get"):
            return False
        if name.startswith("Check"):
            return False
        if name.startswith("Read"):
            return False
        if name.startswith("Ping"):
            return False
        if "SetTyping" in name:
            return False
        if "SendScreenshot" in name:
            return False
        if name.startswith("Upload") and "Profile" not in name:
            return False

        return True

    async def invoke(
        self: "pyrogram.Client",
        query: TLObject[ReturnType],
        retries: int = Session.MAX_RETRIES,
        timeout: float = Session.WAIT_TIMEOUT,
        sleep_threshold: float = None,
        business_connection_id: Optional[str] = None
    ) -> ReturnType:
        """Invoke raw Telegram functions.

        This method makes it possible to manually call every single Telegram API method in a low-level manner.
        Available functions are listed in the :obj:`functions <pyrogram.raw.functions>` package and may accept compound
        data types from :obj:`types <pyrogram.raw.types>` as well as bare types such as ``int``, ``str``, etc...

        .. note::

            This is a utility method intended to be used **only** when working with raw
            :obj:`functions <pyrogram.raw.functions>` (i.e: a Telegram API method you wish to use which is not
            available yet in the Client class as an easy-to-use method).

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            query (``RawFunction``):
                The API Schema function filled with proper arguments.

            retries (``int``):
                Number of retries.

            timeout (``float``):
                Timeout in seconds.

            sleep_threshold (``float``):
                Sleep threshold in seconds.

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection on behalf of which the query is sent.

        Returns:
            ``RawType``: The raw type response generated by the query.

        Raises:
            :obj:`~pyrogram.errors.RPCError`: In case of a Telegram RPC error.

        """
        if not self.is_connected:
            raise ConnectionError("Client has not been started yet")

        if self.no_updates:
            query = raw.functions.InvokeWithoutUpdates(query=query)
        elif getattr(self, "auto_no_updates", False) and not self._auto_needs_updates(query):
            query = raw.functions.InvokeWithoutUpdates(query=query)

        if self.takeout_id:
            query = raw.functions.InvokeWithTakeout(takeout_id=self.takeout_id, query=query)

        if business_connection_id:
            query = raw.functions.InvokeWithBusinessConnection(
                connection_id=business_connection_id,
                query=query
            )

        rate_limiter = getattr(self, "rate_limiter", None)
        if rate_limiter is not None and not rate_limiter.is_closed:
            category = self._classify_query(query)
            await rate_limiter.acquire(category)

        r = await self.session.invoke(
            query, retries, timeout,
            (sleep_threshold
             if sleep_threshold is not None
             else self.sleep_threshold)
        )

        try:
            await self.fetch_peers(getattr(r, "users", []))
        except Exception:
            log.exception("Failed to fetch peers from users")

        try:
            await self.fetch_peers(getattr(r, "chats", []))
        except Exception:
            log.exception("Failed to fetch peers from chats")

        return r
