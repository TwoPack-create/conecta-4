import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.config import get_settings
from app.db.session import AsyncSessionLocal
from app.services.chat_service import authenticate_websocket, ensure_trip_membership, manager, persist_trip_message

router = APIRouter(prefix="/chat", tags=["chat"])


@router.websocket("/ws/trips/{trip_id}")
async def trip_chat_ws(websocket: WebSocket, trip_id: uuid.UUID) -> None:
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return

    settings = get_settings()
    room = str(trip_id)

    async with AsyncSessionLocal() as session:
        try:
            user = await authenticate_websocket(token, session, settings)
            await ensure_trip_membership(session, trip_id, user)
            await manager.connect(room, websocket)
            await manager.broadcast(room, {"type": "system", "message": f"{user.id} joined", "trip_id": room})

            while True:
                text = await websocket.receive_text()
                await persist_trip_message(session, trip_id, user, text)
                await manager.broadcast(
                    room,
                    {
                        "type": "message",
                        "trip_id": room,
                        "sender_id": str(user.id),
                        "message": text,
                    },
                )
        except WebSocketDisconnect:
            manager.disconnect(room, websocket)
        except Exception:
            manager.disconnect(room, websocket)
            await websocket.close(code=1008)
