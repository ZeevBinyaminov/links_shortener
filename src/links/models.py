from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel

from src.core.time import now_moscow


class Url(SQLModel, table=True):
    __tablename__ = "urls"
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str = Field(nullable=False, unique=True)
    short_code: str | None = Field(nullable=True, unique=True)
    alias: str | None = Field(nullable=True, unique=True)
    created_at: datetime = Field(
        default_factory=now_moscow,
        sa_type=DateTime(timezone=True),
    )
    expires_at: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),
    )
    user_id: int | None = Field(
        default=None, foreign_key="users.id", nullable=True)


class Stats(SQLModel, table=True):
    __tablename__ = "stats"
    id: Optional[int] = Field(default=None, primary_key=True)
    short_code: str | None = Field(nullable=True)
    redirected_at: datetime = Field(
        default_factory=now_moscow,
        sa_type=DateTime(timezone=True),
    )
