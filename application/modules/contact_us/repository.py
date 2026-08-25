from sqlalchemy import asc, delete, desc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from application.modules.contact_us.models import ContactUs
from application.modules.contact_us.schemas import (
    CreateContactUsRequest,
    EditContactUsRequest,
)


class ContactUsRepository:
    VALID_ORDERING_CHOICES = {
        "id": asc(ContactUs.id),
        "-id": desc(ContactUs.id),
    }

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_contact_us_repository(self, contact_us_id: int):
        result = await self.session.execute(
            select(
                ContactUs.id,
                ContactUs.phone_number,
                ContactUs.subject,
                ContactUs.message,
                ContactUs.created_at,
                ContactUs.updated_at,
            ).where(ContactUs.id == contact_us_id)
        )
        return result.first()

    async def get_all_contact_us_repository(
        self,
        limit: int,
        offset: int,
        order_by: str,
        search: str,
    ):
        query = (
            select(
                ContactUs.id,
                ContactUs.phone_number,
                ContactUs.subject,
                ContactUs.message,
                ContactUs.created_at,
                ContactUs.updated_at,
            )
            .limit(limit)
            .offset(offset)
            .order_by(self.VALID_ORDERING_CHOICES[order_by])
        )
        if search:
            query = query.where(
                or_(
                    ContactUs.subject.ilike(f"%{search}%"),
                    ContactUs.phone_number.ilike(f"%{search}%"),
                )
            )
        result = await self.session.execute(query)
        return result.all()

    async def count_all_contact_us(self, search: str):
        query = select(func.count(ContactUs.id))
        if search:
            query = query.where(
                or_(
                    ContactUs.subject.ilike(f"%{search}%"),
                    ContactUs.phone_number.ilike(f"%{search}%"),
                )
            )
        result = await self.session.execute(query)
        return result.scalar_one()

    @classmethod
    def valid_order_by(cls, order_by: str):
        return order_by in cls.VALID_ORDERING_CHOICES

    async def create_contact_us_repository(self, payload: CreateContactUsRequest):
        self.session.add(ContactUs(**payload.model_dump()))
        await self.session.commit()

    async def edit_contact_us_repository(
        self,
        payload: EditContactUsRequest,
        contact_us_id: int,
    ):
        data = payload.model_dump(exclude_none=True, exclude_unset=True)
        if not data:
            return
        await self.session.execute(
            update(ContactUs).where(ContactUs.id == contact_us_id).values(**data)
        )
        await self.session.commit()

    async def delete_contact_us_repository(self, contact_us_id: int):
        await self.session.execute(
            delete(ContactUs).where(ContactUs.id == contact_us_id)
        )
        await self.session.commit()
