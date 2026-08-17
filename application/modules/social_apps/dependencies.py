from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from application.core.database import get_db
from application.modules.social_apps.models import SocialApps
from application.modules.social_apps.repository import SocialAppRepository
from application.modules.social_apps.services import SocialAppServices


async def social_app_services_dp(
    session: AsyncSession = Depends(get_db),
) -> SocialAppServices:
    return SocialAppServices(SocialAppRepository(session))


async def check_social_app_existence_by_id_dp(
    social_app_id: int,
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(SocialApps.id).where(SocialApps.id == social_app_id)
    )
    existing_id = result.scalar_one_or_none()
    if existing_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="We do not have such this social app in our database",
        )
    return existing_id
