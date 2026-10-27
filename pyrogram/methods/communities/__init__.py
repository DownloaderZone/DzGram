#  DzGram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#  Copyright (C) 2024-present Downloader Zone <https://github.com/DownloaderZone>
#
#  This file is part of DzGram, a fork of Pyrogram.
#
#  DzGram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  DzGram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with DzGram.  If not, see <http://www.gnu.org/licenses/>.

from .create_community import CreateCommunity
from .get_community_participant_joined_chats import GetCommunityParticipantJoinedChats
from .get_community_peer_link_requests import GetCommunityPeerLinkRequests
from .get_joined_communities import GetJoinedCommunities
from .toggle_all_community_peer_link_request_approval import ToggleAllCommunityPeerLinkRequestApproval
from .toggle_community_collapsed_in_dialogs import ToggleCommunityCollapsedInDialogs
from .toggle_community_participant_banned import ToggleCommunityParticipantBanned
from .toggle_community_peer_link import ToggleCommunityPeerLink
from .toggle_community_peer_link_request_approval import ToggleCommunityPeerLinkRequestApproval


class Communities(
    CreateCommunity,
    GetCommunityParticipantJoinedChats,
    GetCommunityPeerLinkRequests,
    GetJoinedCommunities,
    ToggleAllCommunityPeerLinkRequestApproval,
    ToggleCommunityCollapsedInDialogs,
    ToggleCommunityParticipantBanned,
    ToggleCommunityPeerLink,
    ToggleCommunityPeerLinkRequestApproval,
):
    pass
