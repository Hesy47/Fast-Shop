from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from application.core.database import get_db
from application.modules.scrolls.models import Scroll
from application.modules.scrolls.repository import (
    PublicScrollRepository,
    ScrollRepository,
)
from application.modules.scrolls.services import PublicScrollServices, ScrollServices


async def scroll_services_dp(
    session: AsyncSession = Depends(get_db),
) -> ScrollServices:
    return ScrollServices(ScrollRepository(session))


async def public_scroll_services_dp(
    session: AsyncSession = Depends(get_db),
) -> PublicScrollServices:
    return PublicScrollServices(PublicScrollRepository(session))


async def check_scroll_existence_by_id_dp(
    scroll_id: int,
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(select(Scroll.id).where(Scroll.id == scroll_id))
    existing_id = result.scalar_one_or_none()
    if existing_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="We do not have such this scroll in our database",
        )
    return existing_id
