from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from application.core.database import get_db
from application.modules.contact_us.models import ContactUs
from application.modules.contact_us.repository import ContactUsRepository
from application.modules.contact_us.services import ContactUsServices


async def contact_us_services_dp(
    session: AsyncSession = Depends(get_db),
) -> ContactUsServices:
    return ContactUsServices(ContactUsRepository(session))


async def check_contact_us_existence_by_id_dp(
    contact_us_id: int,
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(ContactUs.id).where(ContactUs.id == contact_us_id)
    )
    existing_id = result.scalar_one_or_none()
    if existing_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="We do not have such this contact-us ticket in our database",
        )
    return existing_id
