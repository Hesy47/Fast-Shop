from typing import Type

from pydantic import BaseModel
from sqlalchemy import and_, asc, delete, desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from application.modules.banners.models import DesktopBannerModel, PhoneBannerModel


class BannerRepository:
    model: Type[DesktopBannerModel] | Type[PhoneBannerModel]

    def __init__(self, session: AsyncSession):
        self.session = session
        self.valid_ordering_choices = {
            "id": asc(self.model.id),
            "-id": desc(self.model.id),
        }

    async def get_public_banner_repository(self, banner_id: int):
        query = select(self.model.id, self.model.title, self.model.image).where(
            self.model.id == banner_id
        )
        result = await self.session.execute(query)
        return result.first()

    async def get_public_all_banners_repository(
        self,
        limit: int,
        offset: int,
        order_by: str,
        search: str,
    ):
        query = (
            select(self.model.id, self.model.title, self.model.image)
            .limit(limit)
            .offset(offset)
            .order_by(self.valid_ordering_choices[order_by])
        )
        if search:
            query = query.where(self.model.title.ilike(f"%{search}%"))
        result = await self.session.execute(query)
        return result.all()

    async def get_banner_repository(self, banner_id: int):
        query = select(
            self.model.id,
            self.model.title,
            self.model.image,
            self.model.created_at,
            self.model.updated_at,
        ).where(self.model.id == banner_id)
        result = await self.session.execute(query)
        return result.first()

    async def get_all_banners_repository(
        self,
        limit: int,
        offset: int,
        order_by: str,
        search: str,
    ):
        query = (
            select(
                self.model.id,
                self.model.title,
                self.model.image,
                self.model.created_at,
                self.model.updated_at,
            )
            .limit(limit)
            .offset(offset)
            .order_by(self.valid_ordering_choices[order_by])
        )
        if search:
            query = query.where(self.model.title.ilike(f"%{search}%"))
        result = await self.session.execute(query)
        return result.all()

    async def count_all_banners(self, search: str):
        query = select(func.count(self.model.id))
        if search:
            query = query.where(self.model.title.ilike(f"%{search}%"))
        result = await self.session.execute(query)
        return result.scalar_one()

    def valid_order_by(self, order_by: str):
        return order_by in self.valid_ordering_choices

    async def check_unique_title_for_create(self, title: str):
        query = select(self.model.id).where(self.model.title == title)
        result = await self.session.execute(query)
        return result.first()

    async def check_unique_image_for_create(self, image: str):
        query = select(self.model.id).where(self.model.image == image)
        result = await self.session.execute(query)
        return result.first()

    async def create_banner_repository(self, payload: BaseModel):
        self.session.add(self.model(**payload.model_dump()))
        await self.session.commit()

    async def check_unique_title_for_edit(self, title: str, banner_id: int):
        query = select(self.model.id).where(
            and_(self.model.title == title, self.model.id != banner_id)
        )
        result = await self.session.execute(query)
        return result.first()

    async def check_unique_image_for_edit(self, image: str, banner_id: int):
        query = select(self.model.id).where(
            and_(self.model.image == image, self.model.id != banner_id)
        )
        result = await self.session.execute(query)
        return result.first()

    async def edit_banner_repository(self, payload: BaseModel, banner_id: int):
        data = payload.model_dump(exclude_none=True, exclude_unset=True)
        if not data:
            return
        query = update(self.model).where(self.model.id == banner_id).values(**data)
        await self.session.execute(query)
        await self.session.commit()

    async def delete_banner_repository(self, banner_id: int):
        query = delete(self.model).where(self.model.id == banner_id)
        await self.session.execute(query)
        await self.session.commit()


class DesktopBannerRepository(BannerRepository):
    model = DesktopBannerModel


class PhoneBannerRepository(BannerRepository):
    model = PhoneBannerModel
