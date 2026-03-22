from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from src.core.time import one_hour_from_now_utc_plus_3


class LinkCreate(BaseModel):
    url: HttpUrl
    alias: str | None = None
    expires_at: datetime | None = Field(default_factory=one_hour_from_now_utc_plus_3)

    @field_validator("alias")
    @classmethod
    def validate_alias(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if value == "":
            return None
        if not value.isalnum():
            raise ValueError("Alias must contain only letters and digits.")
        return value

    @field_validator("expires_at")
    @classmethod
    def normalize_expires_at(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        return value.replace(second=0, microsecond=0)


class LinkUpdate(BaseModel):
    url: HttpUrl | None = None
    alias: str | None = None

    @field_validator("alias")
    @classmethod
    def validate_alias(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if value == "":
            return None
        if not value.isalnum():
            raise ValueError("Alias must contain only letters and digits.")
        return value


class LinkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    short_code: str | None
    alias: str | None
    created_at: datetime
    expires_at: datetime
    user_id: int | None


class LinkStatsRead(BaseModel):
    url: str
    created_at: datetime
    redirects_count: int
    last_used_at: datetime | None
