from __future__ import annotations
from typing import AsyncIterator, Optional
import json
import redis.asyncio as redis
from app.core.settings import settings

class RedisBroker:
    def __init__(self, url: Optional[str] = None) -> None:
        self.url = url or settings.REDIS_URL
        self._client: Optional[redis.Redis] = None

    async def connect(self) -> None:
        if not self._client:
            self._client = redis.from_url(self.url, decode_responses=True)
            # ping to validate the connection
            await self._client.ping()

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def publish(self, channel: str, message: dict) -> None:
        await self.connect()
        assert self._client
        await self._client.publish(channel, json.dumps(message, separators=(",", ":")))

    async def subscribe(self, channel: str) -> AsyncIterator[dict]:
        await self.connect()
        assert self._client
        pubsub = self._client.pubsub()
        await pubsub.subscribe(channel)
        try:
            async for raw in pubsub.listen():
                if raw is None:  # safety check
                    continue
                if raw.get("type") != "message":
                    continue
                data = raw.get("data")
                if not data:
                    continue
                try:
                    yield json.loads(data)
                except Exception:
                    # non-JSON message: ignore
                    continue
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.aclose()