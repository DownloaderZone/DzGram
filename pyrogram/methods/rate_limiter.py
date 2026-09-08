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
import time
from typing import Dict, Optional


class TokenBucket:
    """Async token bucket used to pace API calls and media requests.

    .. note::

        This is the full-featured bucket backing :obj:`RateLimiter`.
        The minimal :obj:`pyrogram.Client.TokenBucket` used by the
        download pacing code is kept intact for backward compatibility.
    """

    def __init__(self, rate: float, burst: Optional[float] = None):
        self._rate = rate
        self._burst = burst if burst is not None else rate
        self._tokens = float(self._burst)
        self._last_refill = time.monotonic()
        self._lock = asyncio.Lock()
        self._total_taken = 0

    @property
    def rate(self) -> float:
        return self._rate

    @rate.setter
    def rate(self, value: float):
        self._refill()
        self._rate = value

    @property
    def available(self) -> float:
        self._refill()
        return self._tokens

    def _refill(self):
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self._burst, self._tokens + elapsed * self._rate)
        self._last_refill = now

    def _try_consume(self, tokens: float = 1.0) -> bool:
        self._refill()
        if self._tokens >= tokens:
            self._tokens -= tokens
            self._total_taken += tokens
            return True
        return False

    def _wait_time(self, tokens: float = 1.0) -> float:
        self._refill()
        if self._tokens >= tokens:
            return 0.0
        return (tokens - self._tokens) / max(self._rate, 0.0001)

    async def acquire(self, tokens: float = 1.0):
        # The wait is served holding the lock. Sleeping outside it woke every
        # waiter at once for one token, and a deficit of a fraction of a token
        # makes that wait microseconds long - a spin, under exactly the load the
        # limiter exists for. asyncio.Lock hands the lock over in order, so this
        # is also what makes admission first-come-first-served.
        async with self._lock:
            while True:
                self._refill()

                if self._tokens >= tokens:
                    self._tokens -= tokens
                    self._total_taken += tokens
                    return

                await asyncio.sleep((tokens - self._tokens) / max(self._rate, 0.0001))

    def congestion(self) -> float:
        if self._burst <= 0:
            return 0.0
        return 1.0 - (self.available / self._burst)


class RateLimiter:
    """Per-category client-side rate limiter.

    Passing any value (even an empty dict) for the client's ``rate_limits``
    parameter enables it with the given limits (or the built-in per-category
    defaults). The limiter is **disabled by default**; leaving ``rate_limits``
    as ``None`` sends without client-side throttling, letting Telegram's
    server-side FloodWait handling (see ``sleep_threshold``) manage the pace.
    """

    CATEGORY_MESSAGE = "message"
    CATEGORY_MEDIA = "media"
    CATEGORY_QUERY = "query"
    CATEGORY_ADMIN = "admin"
    CATEGORY_BULK = "bulk"
    CATEGORY_ACCOUNT = "account"

    DEFAULT_LIMITS = {
        CATEGORY_MESSAGE: {"rate": 20.0, "burst": 30.0},
        CATEGORY_MEDIA: {"rate": 5.0, "burst": 10.0},
        CATEGORY_QUERY: {"rate": 30.0, "burst": 50.0},
        CATEGORY_ADMIN: {"rate": 15.0, "burst": 20.0},
        CATEGORY_BULK: {"rate": 3.0, "burst": 5.0},
        CATEGORY_ACCOUNT: {"rate": 10.0, "burst": 15.0},
    }

    def __init__(self, limits: Optional[Dict[str, Dict[str, float]]] = None):
        resolved = {k: dict(v) for k, v in self.DEFAULT_LIMITS.items()}
        if limits:
            for cat, cfg in limits.items():
                if cat in resolved:
                    resolved[cat].update(cfg)
                else:
                    resolved[cat] = cfg

        self._buckets: Dict[str, TokenBucket] = {}
        self._global = TokenBucket(
            rate=resolved.get("global", {}).get("rate", 30.0),
            burst=resolved.get("global", {}).get("burst", 40.0),
        )
        for cat, cfg in resolved.items():
            if cat == "global":
                continue
            self._buckets[cat] = TokenBucket(
                rate=cfg.get("rate", 30.0),
                burst=cfg.get("burst", cfg.get("rate", 30.0)),
            )

        self._closed = False

    async def acquire(self, category: str, tokens: float = 1.0):
        if self._closed:
            return
        bucket = self._buckets.get(category)
        if bucket:
            await bucket.acquire(tokens)
        await self._global.acquire(tokens)

    def acquire_nowait(self, category: str, tokens: float = 1.0) -> bool:
        if self._closed:
            return True
        bucket = self._buckets.get(category)
        if bucket:
            saved = (bucket._last_refill, bucket._tokens)
            if not bucket._try_consume(tokens):
                return False
            if not self._global._try_consume(tokens):
                bucket._last_refill, bucket._tokens = saved
                bucket._total_taken -= tokens
                return False
        else:
            if not self._global._try_consume(tokens):
                return False
        return True

    def congestion(self) -> float:
        scores = [b.congestion() for b in self._buckets.values()]
        scores.append(self._global.congestion())
        return max(scores) if scores else 0.0

    @property
    def available(self) -> Dict[str, float]:
        result = {k: b.available for k, b in self._buckets.items()}
        result["global"] = self._global.available
        return result

    async def close(self):
        self._closed = True

    def reopen(self):
        self._closed = False

    @property
    def is_closed(self) -> bool:
        return self._closed

    def update_limits(self, category: str, rate: float, burst: float):
        if category == "global":
            old = self._global
            self._global = TokenBucket(rate=rate, burst=burst)
            self._global._tokens = min(old._tokens, burst)
            self._global._total_taken = old._total_taken
        else:
            old = self._buckets.get(category)
            self._buckets[category] = TokenBucket(rate=rate, burst=burst)
            if old:
                self._buckets[category]._tokens = min(old._tokens, burst)
                self._buckets[category]._total_taken = old._total_taken
