from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from src.core.time import now_utc_plus_3


class Url(SQLModel, table=True):
    __tablename__ = "urls"
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str = Field(nullable=False, unique=True)
    short_code: str | None = Field(nullable=True, unique=True)
    alias: str | None = Field(nullable=True, unique=True)
    created_at: datetime = Field(
        default_factory=now_utc_plus_3,
        sa_type=DateTime(timezone=True),
    )
    expires_at: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),
    )
    user_id: int | None = Field(
        default=None, foreign_key="users.id", nullable=True)
    stats: list["Stats"] = Relationship(
        back_populates="url",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class Stats(SQLModel, table=True):
    __tablename__ = "stats"
    id: Optional[int] = Field(default=None, primary_key=True)
    url_id: int = Field(foreign_key="urls.id", nullable=False)
    redirected_at: datetime = Field(
        default_factory=now_utc_plus_3,
        sa_type=DateTime(timezone=True),
    )
    url: Url = Relationship(back_populates="stats")
