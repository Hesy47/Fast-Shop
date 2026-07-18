from sqlalchemy import and_, asc, desc, func, or_, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from application.modules.collections.models import Collection
from application.modules.collections.schemas import (
    CreateCollectionRequest,
    EditCollectionRequest,
)


class CollectionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def check_is_unique_title_repository_for_create(self, title: str):
        is_unique_query = select(Collection.id).where(Collection.title == title)
        is_unique_operation = await self.session.execute(is_unique_query)
        is_unique_result = is_unique_operation.first()

        return is_unique_result

    async def check_is_unique_image_repository_for_create(self, image: str):
        is_unique_query = select(Collection.id).where(Collection.image == image)
        is_unique_operation = await self.session.execute(is_unique_query)
        is_unique_result = is_unique_operation.first()

        return is_unique_result

    async def create_collection_repository(self, payload: CreateCollectionRequest):
        new_collection = Collection(**payload.model_dump())

        self.session.add(new_collection)
        await self.session.commit()
