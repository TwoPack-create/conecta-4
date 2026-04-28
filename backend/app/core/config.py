from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Conecta FCFM API"
    environment: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    database_url: str = Field(..., alias="DATABASE_URL")

    supabase_url: str = Field(..., alias="SUPABASE_URL")
    supabase_jwt_audience: str = Field(default="authenticated", alias="SUPABASE_JWT_AUDIENCE")

    fuel_price_clp: float = Field(default=1300, alias="FUEL_PRICE_CLP")
    platform_fee_pct: float = Field(default=0.10, alias="PLATFORM_FEE_PCT")

    accompaniment_checker_interval_seconds: int = Field(default=60, alias="ACCOMPANIMENT_CHECKER_INTERVAL_SECONDS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
