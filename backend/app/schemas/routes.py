import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class CreateRouteReportRequest(BaseModel):
    tipo_reporte: Literal["ruta_insegura", "incidente", "ruta_segura"]
    nivel_riesgo: Literal["bajo", "medio", "alto"]
    ubicacion: str = Field(min_length=3)
    descripcion: str = Field(min_length=3)
    lat: Decimal | None = None
    lng: Decimal | None = None


class RouteReportResponse(BaseModel):
    id: uuid.UUID
    tipo_reporte: str
    nivel_riesgo: str
    ubicacion: str
    descripcion: str
    created_at: datetime


class VoteRouteReportRequest(BaseModel):
    vote: Literal[-1, 1]


class VoteRouteReportResponse(BaseModel):
    report_id: uuid.UUID
    voter_user_id: uuid.UUID
    vote: int
