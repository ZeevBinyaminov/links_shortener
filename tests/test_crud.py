import asyncio
from datetime import timedelta

import pytest
from sqlalchemy import delete as sa_delete
from sqlmodel import select

from conftest import async_session_maker
from src.core.config import INACTIVE_LINK_DAYS
from src.core.time import days_ago_utc_plus_3, now_utc_plus_3
from src.links.crud import (
    create_link,
    create_redirect_stat,
    delete_if_expired,
    delete_if_inactive,
    delete_link,
    get_link_by_alias,
    get_link_by_id,
    get_link_by_short_code,
    get_link_by_url,
    get_link_stats,
    get_links_by_user,
    update_link,
)
from src.auth.models import User
from src.links.models import Stats, Url


from tests.conftest import _cleanup_db


@pytest.fixture(autouse=True, scope="function")
def clean_db():
    asyncio.run(_cleanup_db())


async def _create_user(session, email: str | None = None) -> User:
    user = User(
        email="test@test.ru",
        hashed_password="hashed-password",
        is_active=True,
        is_superuser=False,
        is_verified=False,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest.mark.anyio
async def test_create_and_get_link_by_id_url_short_code():
    async with async_session_maker() as session:
        link = await create_link(
            session,
            original_url=f"https://example.com/",
        )

        by_id = await get_link_by_id(session, link.id)
        by_url = await get_link_by_url(session, link.url)
        by_short_code = await get_link_by_short_code(session, link.short_code)

        assert link.id is not None
        assert link.short_code is not None
        assert by_id.id == link.id
        assert by_url.id == link.id
        assert by_short_code.id == link.id


@pytest.mark.anyio
async def test_create_link_with_alias_and_get_by_alias():
    async with async_session_maker() as session:
        alias = f"test_alias"
        link = await create_link(
            session,
            original_url="https://example.com/2",
            alias=alias,
        )

        by_alias = await get_link_by_alias(session, alias)

        assert link.short_code == alias
        assert by_alias.id == link.id


@pytest.mark.anyio
async def test_update_link_changes_url_and_alias():
    async with async_session_maker() as session:
        url = "https://example.com/"
        link = await create_link(
            session,
            original_url=url,
        )
        new_alias = "new_alias"

        updated = await update_link(
            session,
            link,
            original_url=url,
            alias=new_alias,
        )

        assert updated.url == url
        assert updated.alias == new_alias
        assert updated.short_code == new_alias


@pytest.mark.anyio
async def test_create_redirect_stat_and_get_stats():
    async with async_session_maker() as session:
        link = await create_link(
            session,
            original_url=f"https://example.com/",
        )

        stat_1 = await create_redirect_stat(session, link)
        stat_2 = await create_redirect_stat(session, link)
        redirects_count, last_used_at = await get_link_stats(session, link)

        assert stat_1.id is not None
        assert stat_2.id is not None
        assert redirects_count == 2
        assert last_used_at is not None


@pytest.mark.anyio
async def test_delete_link_removes_link_and_stats():
    async with async_session_maker() as session:
        link = await create_link(
            session,
            original_url=f"https://example.com/",
        )
        await create_redirect_stat(session, link)

        await delete_link(session, link)

        deleted_link = await get_link_by_id(session, link.id)
        remaining_stats = await session.execute(
            select(Stats).where(
                Stats.url_id == link.id)
        )

        assert deleted_link is None
        assert remaining_stats.scalars().all() == []


@pytest.mark.anyio
async def test_delete_if_expired_removes_expired_link():
    async with async_session_maker() as session:
        link = await create_link(
            session,
            original_url=f"https://example.com/",
            expires_at=now_utc_plus_3() - timedelta(minutes=1),
        )

        deleted = await delete_if_expired(session, link)
        deleted_link = await get_link_by_id(session, link.id)

        assert deleted == True
        assert deleted_link is None


@pytest.mark.anyio
async def test_get_links_by_user_returns_only_active_links():
    async with async_session_maker() as session:
        user = await _create_user(session)
        active_link = await create_link(
            session,
            original_url="https://example.com/active",
            user_id=user.id,
            expires_at=now_utc_plus_3() + timedelta(days=1),
        )
        inactive_link = await create_link(
            session,
            original_url="https://example.com/inactive",
            user_id=user.id,
        )

        expired_link = await create_link(
            session,
            original_url="https://example.com/expired",
            user_id=user.id,
            expires_at=now_utc_plus_3() - timedelta(minutes=1),
        )

        inactive_link.created_at = days_ago_utc_plus_3(
            INACTIVE_LINK_DAYS + 1)
        session.add(inactive_link)
        session.add(expired_link)

        await session.commit()
        await session.refresh(inactive_link)
        await session.refresh(expired_link)

        links = await get_links_by_user(session, user.id)
        not_deleted_and_expired = await get_link_by_id(session, active_link.id)
        deleted_inactive = await get_link_by_id(session, inactive_link.id)
        deleted_expired = await get_link_by_id(session, expired_link.id)

        assert [link.id for link in links] == [active_link.id]
        assert not_deleted_and_expired is not None
        assert deleted_inactive is None
        assert deleted_expired is None


@pytest.mark.anyio
async def test_non_existent_link():
    async with async_session_maker() as session:
        user = await _create_user(session)
        non_existent_link = await get_link_by_id(session, 9999)

        assert non_existent_link is None
