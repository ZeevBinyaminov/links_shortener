from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.deps import current_user, optional_current_user
from src.auth.models import User
from src.core.cache import delete_link_cache, get_link_cache, set_link_cache
from src.core.db import get_db
from src.links.crud import (
    create_link,
    create_redirect_stat,
    delete_if_expired,
    delete_if_inactive,
    delete_link,
    get_link_by_short_code,
    get_link_by_url,
    get_links_by_user,
    get_link_stats,
    update_link,
)
from src.links.models import Url
from src.links.schemas import LinkCreate, LinkRead, LinkStatsRead, LinkUpdate


router = APIRouter(prefix="/links", tags=["links"])


async def get_owned_link(
    short_code: str,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
) -> Url:
    link = await get_link_by_short_code(session, short_code)
    if await delete_if_expired(session, link):
        link = None
    if await delete_if_inactive(session, link):
        link = None
    if link is None or link.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Link not found.")
    return link


@router.post("/shorten", response_model=LinkRead, status_code=status.HTTP_201_CREATED)
async def create_user_link(
    payload: LinkCreate,
    session: AsyncSession = Depends(get_db),
    user: User | None = Depends(optional_current_user),
) -> Url:
    try:
        return await create_link(
            session=session,
            original_url=str(payload.url),
            user_id=user.id if user is not None else None,
            alias=payload.alias,
            expires_at=payload.expires_at,
        )
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Alias or URL already exists.",
        )


@router.get("/my", response_model=list[LinkRead])
async def list_my_links(
    session: AsyncSession = Depends(get_db),
    user: User | None = Depends(optional_current_user),
) -> list[Url]:
    if user is None:
        return []
    return await get_links_by_user(session, user.id)


@router.get("/search", response_model=LinkRead)
async def search_link_by_original_url(
    original_url: str,
    session: AsyncSession = Depends(get_db),
) -> Url:
    link = await get_link_by_url(session, original_url)
    if await delete_if_expired(session, link):
        link = None
    if await delete_if_inactive(session, link):
        link = None
    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found.",
        )
    return link


@router.get("/{short_code}/stats", response_model=LinkStatsRead)
async def get_short_code_stats(
    short_code: str,
    session: AsyncSession = Depends(get_db),
) -> LinkStatsRead:
    link = await get_link_by_short_code(session, short_code)
    if await delete_if_expired(session, link):
        link = None
    if await delete_if_inactive(session, link):
        link = None
    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found.",
        )

    redirects_count, last_used_at = await get_link_stats(session, short_code)
    return LinkStatsRead(
        url=link.url,
        created_at=link.created_at,
        redirects_count=redirects_count,
        last_used_at=last_used_at,
    )


@router.get("/{short_code}")
async def get_my_link(
    short_code: str,
    session: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    cached_url = await get_link_cache(short_code)
    if cached_url is not None:
        await create_redirect_stat(session, short_code)
        return RedirectResponse(url=cached_url, status_code=status.HTTP_302_FOUND)

    link = await get_link_by_short_code(session, short_code)
    if await delete_if_expired(session, link):
        link = None
    if await delete_if_inactive(session, link):
        link = None
    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found.",
        )
    await set_link_cache(short_code, link.url)
    await create_redirect_stat(session, short_code)
    return RedirectResponse(url=link.url, status_code=status.HTTP_302_FOUND)


@router.put("/{short_code}", response_model=LinkRead)
async def update_my_link(
    payload: LinkUpdate,
    link: Url = Depends(get_owned_link),
    session: AsyncSession = Depends(get_db),
) -> Url:
    old_short_code = link.short_code
    try:
        updated_link = await update_link(
            session=session,
            link=link,
            original_url=str(payload.url) if payload.url is not None else None,
            alias=payload.alias,
        )
        if old_short_code is not None:
            await delete_link_cache(old_short_code)
        if updated_link.short_code is not None:
            await set_link_cache(updated_link.short_code, updated_link.url)
        return updated_link
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Alias or URL already exists.",
        )


@router.delete("/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_link(
    link: Url = Depends(get_owned_link),
    session: AsyncSession = Depends(get_db),
) -> Response:
    if link.short_code is not None:
        await delete_link_cache(link.short_code)
    await delete_link(session, link)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
