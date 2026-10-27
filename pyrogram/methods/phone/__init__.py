
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

from .load_group_call_participants import LoadGroupCallParticipants
from .invite_group_call_participants import InviteGroupCallParticipants
from .create_video_chat import CreateVideoChat
from .discard_group_call import DiscardGroupCall
from .get_video_chat_rtmp_url import GetVideoChatRtmpUrl


class Phone(
    InviteGroupCallParticipants,
    LoadGroupCallParticipants,
    CreateVideoChat,
    DiscardGroupCall,
    GetVideoChatRtmpUrl,
):
    pass
