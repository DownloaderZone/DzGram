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
import logging

import pyrogram
from pyrogram import raw

log = logging.getLogger(__name__)


class Terminate:
    async def terminate(
        self: "pyrogram.Client",
    ):
        """Terminate the client by shutting down workers.

        This method does the opposite of :meth:`~pyrogram.Client.initialize`.
        It will stop the dispatcher and shut down updates and download workers.

        Raises:
            ConnectionError: In case you try to terminate a client that is already terminated.

        """
        if not self.is_initialized:
            raise ConnectionError("Client is already terminated")

        if self.takeout_id:
            await self.invoke(raw.functions.account.FinishTakeoutSession())
            log.info("Takeout session %s finished", self.takeout_id)

        await self.storage.save()
        await self.dispatcher.stop()

        for media_session in self.media_sessions.values():
            try:
                await media_session.stop()
            except Exception:
                log.exception("Error stopping media session")

        self.media_sessions.clear()

        for upload_sessions in self.upload_sessions.values():
            for upload_session in upload_sessions:
                try:
                    await upload_session.stop()
                except Exception:
                    log.exception("Error stopping upload session")

        self.upload_sessions.clear()

        for pool in getattr(self, "media_session_pools", {}).values():
            for pooled_session in pool:
                # Pooled sessions are distinct from the cached primary in
                # media_sessions (created via _make_media_session).
                try:
                    await pooled_session.stop()
                except Exception:
                    log.exception("Error stopping pooled media session")

        if hasattr(self, "media_session_pools"):
            self.media_session_pools.clear()

        for session in getattr(self, "sessions", {}).values():
            try:
                await session.stop()
            except Exception:
                log.exception("Error stopping session")

        if hasattr(self, "sessions"):
            self.sessions.clear()

        if getattr(self, "media_pool_reaper_task", None) is not None:
            self.media_pool_reaper_event.set()

            try:
                await self.media_pool_reaper_task
            except Exception:
                pass

            self.media_pool_reaper_event.clear()
            self.media_pool_reaper_task = None

        self.updates_watchdog_event.set()

        if self.updates_watchdog_task is not None:
            try:
                await self.updates_watchdog_task
            except asyncio.CancelledError:
                pass
            except Exception:
                # Watchdog does best-effort GetState probes; a failure
                # here (e.g. connection already closed) must not fail
                # terminate()/stop() and break auto-restart flows.
                log.debug("updates_watchdog task failed during terminate", exc_info=True)
            finally:
                self.updates_watchdog_task = None

        self.updates_watchdog_event.clear()

        self.is_initialized = False
