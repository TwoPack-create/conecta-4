import json
import uuid
from collections import defaultdict
from datetime import UTC, datetime

from fastapi import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.auth import decode_supabase_jwt
from app.models.trip import Trip
from app.schemas.common import AuthenticatedUser


class ConnectionManager:
    def __init__(self) -> None:
        self.rooms: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, room: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.rooms[room].add(websocket)

    def disconnect(self, room: str, websocket: WebSocket) -> None:
        self.rooms[room].discard(websocket)

    async def broadcast(self, room: str, payload: dict) -> None:
        dead = []
        for ws in self.rooms.get(room, set()):
            try:
                await ws.send_text(json.dumps(payload, default=str))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(room, ws)


manager = ConnectionManager()


async def authenticate_websocket(token: str, session: AsyncSession, settings) -> AuthenticatedUser:
    payload = decode_supabase_jwt(token, settings)
    user_id = uuid.UUID(payload["sub"])
    from sqlalchemy import text

    row = (
        await session.execute(
            text("select id, campus_id, is_admin from public.users where id = :uid limit 1"), {"uid": user_id}
        )
    ).mappings().first()
    if not row:
        raise ValueError("User not provisioned")
    return AuthenticatedUser(id=row["id"], campus_id=row["campus_id"], is_admin=row["is_admin"])


async def persist_trip_message(session: AsyncSession, trip_id: uuid.UUID, user: AuthenticatedUser, message: str) -> None:
    await session.execute(
        # SQL text keeps compatibility with current lightweight model mapping.
        __import__("sqlalchemy").text(
            """
            insert into public.trip_messages (id, trip_id, campus_id, sender_id, message, created_at)
            values (:id, :trip_id, :campus_id, :sender_id, :message, :created_at)
            """
        ),
        {
            "id": uuid.uuid4(),
            "trip_id": trip_id,
            "campus_id": user.campus_id,
            "sender_id": user.id,
            "message": message,
            "created_at": datetime.now(UTC),
        },
    )
    await session.commit()


async def ensure_trip_membership(session: AsyncSession, trip_id: uuid.UUID, user: AuthenticatedUser) -> None:
    row = (
        await session.execute(
            __import__("sqlalchemy").text(
                """
                select 1
                from public.trip_participants
                where trip_id = :trip_id and user_id = :user_id and status = 'accepted'
                limit 1
                """
            ),
            {"trip_id": trip_id, "user_id": user.id},
        )
    ).first()
    if not row:
        trip = await session.get(Trip, trip_id)
        if not trip or trip.creator_id != user.id:
            raise ValueError("User is not participant of trip")
