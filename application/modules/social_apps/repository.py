from sqlalchemy import and_, asc, delete, desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from application.modules.social_apps.models import SocialApps
from application.modules.social_apps.schemas import (
    CreateSocialAppRequest,
    EditSocialAppRequest,
)


class SocialAppRepository:
    VALID_ORDERING_CHOICES = {
        "id": asc(SocialApps.id),
        "-id": desc(SocialApps.id),
    }

    def __init__(self, session: AsyncSession):
        self.session = session

    async def public_get_all_social_apps_repository(self):
        result = await self.session.execute(
            select(SocialApps.title, SocialApps.link).order_by(SocialApps.id)
        )
        return result.all()

    async def get_social_app_repository(self, social_app_id: int):
        result = await self.session.execute(
            select(
                SocialApps.id,
                SocialApps.title,
                SocialApps.link,
                SocialApps.created_at,
                SocialApps.updated_at,
            ).where(SocialApps.id == social_app_id)
        )
        return result.first()

    async def get_all_social_apps_repository(
        self,
        limit: int,
        offset: int,
        order_by: str,
        search: str,
    ):
        query = (
            select(
                SocialApps.id,
                SocialApps.title,
                SocialApps.link,
                SocialApps.created_at,
                SocialApps.updated_at,
            )
            .limit(limit)
            .offset(offset)
            .order_by(self.VALID_ORDERING_CHOICES[order_by])
        )
        if search:
            query = query.where(SocialApps.title.ilike(f"%{search}%"))
        result = await self.session.execute(query)
        return result.all()

    async def count_all_social_apps(self, search: str):
        query = select(func.count(SocialApps.id))
        if search:
            query = query.where(SocialApps.title.ilike(f"%{search}%"))
        result = await self.session.execute(query)
        return result.scalar_one()

    @classmethod
    def valid_order_by(cls, order_by: str):
        return order_by in cls.VALID_ORDERING_CHOICES

    async def check_unique_title_for_create(self, title: str):
        result = await self.session.execute(
            select(SocialApps.id).where(SocialApps.title == title)
        )
        return result.first()

    async def create_social_app_repository(self, payload: CreateSocialAppRequest):
        self.session.add(SocialApps(**payload.model_dump()))
        await self.session.commit()

    async def check_unique_title_for_edit(
        self,
        title: str,
        social_app_id: int,
    ):
        result = await self.session.execute(
            select(SocialApps.id).where(
                and_(SocialApps.title == title, SocialApps.id != social_app_id)
            )
        )
        return result.first()

    async def edit_social_app_repository(
        self,
        payload: EditSocialAppRequest,
        social_app_id: int,
    ):
        data = payload.model_dump(exclude_none=True, exclude_unset=True)
        if not data:
            return
        await self.session.execute(
            update(SocialApps).where(SocialApps.id == social_app_id).values(**data)
        )
        await self.session.commit()

    async def delete_social_app_repository(self, social_app_id: int):
        await self.session.execute(
            delete(SocialApps).where(SocialApps.id == social_app_id)
        )
        await self.session.commit()
