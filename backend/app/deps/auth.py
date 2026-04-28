import uuid
from functools import lru_cache

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError, PyJWKClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_db_session
from app.schemas.common import AuthenticatedUser

security = HTTPBearer(auto_error=True)


@lru_cache
def get_jwk_client(supabase_url: str) -> PyJWKClient:
    jwks_url = f"{supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
    return PyJWKClient(jwks_url)


def decode_supabase_jwt(token: str, settings: Settings) -> dict:
    try:
        jwk_client = get_jwk_client(settings.supabase_url)
        signing_key = jwk_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=settings.supabase_jwt_audience,
            options={"require": ["exp", "sub"]},
        )
        return payload
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Supabase JWT",
        ) from exc


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> AuthenticatedUser:
    payload = decode_supabase_jwt(credentials.credentials, settings)

    subject = payload.get("sub")
    if not subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="JWT missing subject")

    try:
        user_id = uuid.UUID(subject)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid subject in JWT") from exc

    query = text(
        """
        select id, campus_id, is_admin
        from public.users
        where id = :user_id
        limit 1
        """
    )
    result = await session.execute(query, {"user_id": user_id})
    row = result.mappings().first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not provisioned in platform")

    return AuthenticatedUser(
        id=row["id"],
        campus_id=row["campus_id"],
        is_admin=row["is_admin"],
    )
