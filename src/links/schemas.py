from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from src.core.time import MOSCOW_TZ, one_hour_from_now_moscow


class LinkCreate(BaseModel):
    url: HttpUrl
    alias: str | None = None
    expires_at: datetime | None = Field(default_factory=one_hour_from_now_moscow)

    @field_validator("expires_at")
    @classmethod
    def normalize_expires_at(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=MOSCOW_TZ)
        return value.replace(second=0, microsecond=0)


class LinkUpdate(BaseModel):
    url: HttpUrl | None = None
    alias: str | None = None


class LinkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    short_code: str | None
    alias: str | None
    created_at: datetime
    expires_at: datetime | None
    user_id: int | None


class LinkStatsRead(BaseModel):
    url: str
    created_at: datetime
    redirects_count: int
    last_used_at: datetime | None
