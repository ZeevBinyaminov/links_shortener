from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.core.config import INACTIVE_LINK_DAYS
from src.core.time import days_ago_utc_plus_3, now_utc_plus_3

from .models import Stats, Url
from .service import decode_short_code, get_short_code


async def create_link(
    session: AsyncSession,
    original_url: str,
    user_id: int | None = None,
    alias: str | None = None,
    expires_at=None,
) -> Url:
    link = Url(
        url=original_url,
        alias=alias,
        user_id=user_id,
        expires_at=expires_at,
    )
    session.add(link)
    await session.flush()

    link.short_code = get_short_code(link.id, alias, user_id)
    await session.commit()
    await session.refresh(link)
    return link


async def get_link_by_id(session: AsyncSession, link_id: int) -> Url | None:
    return await session.get(Url, link_id)


async def get_link_by_short_code(
    session: AsyncSession,
    short_code: str,
) -> Url | None:
    url_id = decode_short_code(short_code)
    statement = select(Url).where(Url.id == url_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def get_link_by_alias(session: AsyncSession, alias: str) -> Url | None:
    statement = select(Url).where(Url.alias == alias)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def get_link_by_url(session: AsyncSession, original_url: str) -> Url | None:
    statement = select(Url).where(Url.url == original_url)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def get_links_by_user(session: AsyncSession, user_id: int) -> list[Url]:
    statement = (
        select(Url)
        .where(Url.user_id == user_id)
        .order_by(Url.created_at.desc())
    )
    result = await session.execute(statement)
    links = list(result.scalars().all())
    active_links: list[Url] = []
    for link in links:
        if await delete_if_expired(session, link):
            continue
        if await delete_if_inactive(session, link):
            continue
        active_links.append(link)
    return active_links


async def update_link(
    session: AsyncSession,
    link: Url,
    original_url: str | None = None,
    alias: str | None = None,
) -> Url:
    if original_url is not None:
        link.url = original_url
    if alias is not None:
        link.alias = alias

    link.short_code = get_short_code(link.id, link.alias, link.user_id)

    session.add(link)
    await session.commit()
    await session.refresh(link)
    return link


async def create_redirect_stat(session: AsyncSession, link: Url) -> Stats:
    stat = Stats(url_id=link.id)
    session.add(stat)
    await session.commit()
    await session.refresh(stat)
    return stat


async def get_link_stats(session: AsyncSession, link: Url) -> tuple[int, object | None]:
    statement = select(
        func.count(Stats.id),
        func.max(Stats.redirected_at),
    ).where(Stats.url_id == link.id)
    result = await session.execute(statement)
    redirects_count, last_used_at = result.one()
    return redirects_count, last_used_at


async def delete_if_expired(session: AsyncSession, link: Url | None) -> bool:
    if link is None or link.expires_at is None:
        return False
    if link.expires_at > now_utc_plus_3():
        return False
    await delete_link(session, link)
    return True


async def delete_if_inactive(session: AsyncSession, link: Url | None) -> bool:
    if link is None:
        return False

    _, last_used_at = await get_link_stats(session, link)
    last_activity_at = last_used_at or link.created_at
    if last_activity_at >= days_ago_utc_plus_3(INACTIVE_LINK_DAYS):
        return False

    await delete_link(session, link)
    return True


async def delete_link(session: AsyncSession, link: Url) -> None:
    await session.delete(link)
    await session.commit()
