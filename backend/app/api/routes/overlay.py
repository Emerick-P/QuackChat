from typing import Optional
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query
from app.core.auth import auth_context
from app.db.uow import UnitOfWork, get_uow
from app.services.overlay import ensure_room_listener, rooms  # our singleton Rooms()
from app.core.jwt import decode_access_token


router = APIRouter(prefix="/overlay", tags=["overlay"])

async def user_from_token(uow: UnitOfWork, token: Optional[str]):
    if not token:
        return None
    try:
        payload = decode_access_token(token)
        sub = payload.get("sub")
        if not sub:
            return None
    except Exception:
        return None
    return await uow.users.get(sub)

@router.websocket("/ws")
async def ws_overlay(ws: WebSocket,
                    channel: str = Query("default", description='Room; "default" = user room'),
                    token: Optional[str] = Query(None, description="JWT token for authentication"),
                    uow: UnitOfWork = Depends(get_uow)):
    # 1. Authenticate the user
    user = await user_from_token(uow, token)
    if not user:
        await ws.close(code=4401, reason="Unauthorized")
        return
    
    # 2. Determine the room name
    room = f"user:{user.id}" if channel == "default" else channel

    # 3. Add the WebSocket to the room and manage the connection
    await rooms.add(ws, room)
    try:
        await ensure_room_listener(room)  # no-op si pas de Redis
        while True:
            await ws.receive_text()  # keep-alive; on ignore les messages entrants
    except WebSocketDisconnect:
        pass
    finally:
        await rooms.remove(ws, room)