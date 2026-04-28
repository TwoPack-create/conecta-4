import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    campus_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("campuses.id"), nullable=False)
    creator_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    mode: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False, default="publicado")

    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    estimated_arrival_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    origin_label: Mapped[str] = mapped_column(nullable=False)
    destination_label: Mapped[str] = mapped_column(nullable=False)
    origin_lat: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    origin_lng: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    destination_lat: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    destination_lng: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))

    route_description: Mapped[str | None] = mapped_column(nullable=True)
    seats_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    seats_available: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_unlimited_capacity: Mapped[bool] = mapped_column(nullable=False, default=False)

    public_transport_mode: Mapped[str | None] = mapped_column(nullable=True)
    line_or_route: Mapped[str | None] = mapped_column(nullable=True)
    direction: Mapped[str | None] = mapped_column(nullable=True)

    vehicle_name: Mapped[str | None] = mapped_column(nullable=True)
    vehicle_model: Mapped[str | None] = mapped_column(nullable=True)
    vehicle_type: Mapped[str | None] = mapped_column(nullable=True)
    vehicle_color: Mapped[str | None] = mapped_column(nullable=True)

    costo_compartido: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    comision_plataforma: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    acepta_encargos: Mapped[bool] = mapped_column(nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
