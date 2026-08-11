from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from application.core.database import get_db
from application.modules.banners.models import DesktopBannerModel, PhoneBannerModel
from application.modules.banners.repository import (
    DesktopBannerRepository,
    PhoneBannerRepository,
)
from application.modules.banners.services import (
    DesktopBannerServices,
    PhoneBannerServices,
)


async def desktop_banner_services_dp(
    session: AsyncSession = Depends(get_db),
) -> DesktopBannerServices:
    return DesktopBannerServices(DesktopBannerRepository(session))


async def phone_banner_services_dp(
    session: AsyncSession = Depends(get_db),
) -> PhoneBannerServices:
    return PhoneBannerServices(PhoneBannerRepository(session))


async def check_desktop_banner_existence_by_id_dp(
    desktop_banner_id: int,
    session: AsyncSession = Depends(get_db),
):
    query = select(DesktopBannerModel.id).where(
        DesktopBannerModel.id == desktop_banner_id
    )
    result = await session.execute(query)
    banner_id = result.scalar_one_or_none()
    if banner_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="We do not have such this desktop banner in our database",
        )
    return banner_id


async def check_phone_banner_existence_by_id_dp(
    phone_banner_id: int,
    session: AsyncSession = Depends(get_db),
):
    query = select(PhoneBannerModel.id).where(
        PhoneBannerModel.id == phone_banner_id
    )
    result = await session.execute(query)
    banner_id = result.scalar_one_or_none()
    if banner_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="We do not have such this phone banner in our database",
        )
    return banner_id
