import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt

from app.constant import ACCESS_TOKEN_COOKIE_NAME
from app.core.config import settings
from ws.manager import notification_manager

ws_router = APIRouter()


def _authenticate(websocket: WebSocket) -> str | None:
    token = websocket.cookies.get(ACCESS_TOKEN_COOKIE_NAME)
    if not token:
        return None
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload.get("user_name")
    except JWTError:
        return None


@ws_router.websocket("/ws/notifications")
async def ws_notifications(websocket: WebSocket) -> None:
    user_name = _authenticate(websocket)
    if not user_name:
        await websocket.close(code=4001)
        return

    await websocket.accept()
    notification_manager.connect(user_name, websocket)

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
                if msg.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except Exception:
                pass
    except WebSocketDisconnect:
        pass
    finally:
        notification_manager.disconnect(user_name, websocket)
