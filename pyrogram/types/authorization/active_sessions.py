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

import pyrogram
from pyrogram import raw, types, utils

from ..object import Object


class ActiveSessions(Object):
    """Contains a list of sessions

    Parameters:
        inactive_session_ttl_days (``int``):
            Number of days of inactivity before sessions will automatically be terminated; 1-366 days.

        active_sessions (List of :obj:`~pyrogram.types.ActiveSession`):
            List of sessions.

    """

    def __init__(
        self,
        *,
        inactive_session_ttl_days: int = None,
        active_sessions: list["types.ActiveSession"] = None
    ):
        super().__init__()

        self.inactive_session_ttl_days = inactive_session_ttl_days
        self.active_sessions = active_sessions

    @staticmethod
    def _parse(
        client: "pyrogram.Client",
        authorizations: "raw.types.account.Authorizations"
    ) -> "ActiveSessions":        
        return ActiveSessions(
            inactive_session_ttl_days=authorizations.authorization_ttl_days,
            active_sessions=types.List([
                types.ActiveSession._parse(client, active)
                for active in authorizations.authorizations
            ])
        )
