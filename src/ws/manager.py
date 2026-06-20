import asyncio
from collections import defaultdict

from fastapi import WebSocket


class NotificationManager:
    def __init__(self):
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)

    def connect(self, user_name: str, ws: WebSocket) -> None:
        self._connections[user_name.lower()].add(ws)

    def disconnect(self, user_name: str, ws: WebSocket) -> None:
        key = user_name.lower()
        self._connections[key].discard(ws)
        if not self._connections[key]:
            self._connections.pop(key, None)

    async def push(self, user_name: str, payload: dict) -> None:
        key = user_name.lower()
        dead: set[WebSocket] = set()
        for ws in list(self._connections.get(key, set())):
            try:
                await ws.send_json(payload)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self._connections[key].discard(ws)

    async def push_to_users(self, user_names: list[str], payload: dict) -> None:
        targets = [u for u in user_names if u]
        if targets:
            await asyncio.gather(
                *(self.push(u, payload) for u in targets),
                return_exceptions=True,
            )


notification_manager = NotificationManager()
