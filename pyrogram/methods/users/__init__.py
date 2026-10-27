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

from .block_user import BlockUser
from .delete_profile_photos import DeleteProfilePhotos
from .get_chat_photos import GetChatPhotos
from .get_chat_photos_count import GetChatPhotosCount
from .get_common_chats import GetCommonChats
from .get_default_emoji_statuses import GetDefaultEmojiStatuses
from .get_me import GetMe
from .get_users import GetUsers
from .set_emoji_status import SetEmojiStatus
from .set_profile_photo import SetProfilePhoto
from .set_username import SetUsername
from .unblock_user import UnblockUser
from .update_profile import UpdateProfile
from .set_birthdate import SetBirthdate
from .set_personal_chat import SetPersonalChat
from .update_status import UpdateStatus
from .delete_account import DeleteAccount


class Users(
    BlockUser,
    DeleteProfilePhotos,
    GetChatPhotos,
    GetChatPhotosCount,
    GetCommonChats,
    GetDefaultEmojiStatuses,
    GetMe,
    GetUsers,
    SetBirthdate,
    SetEmojiStatus,
    SetPersonalChat,
    SetProfilePhoto,
    SetUsername,
    UnblockUser,
    UpdateProfile,
    UpdateStatus,
    DeleteAccount,
):
    pass
