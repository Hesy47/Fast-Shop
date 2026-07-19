from sqlalchemy import and_, asc, desc, func, or_, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from application.modules.collections.models import Collection
from application.modules.collections.schemas import (
    CreateCollectionRequest,
    EditCollectionRequest,
)


class CollectionRepository:
    VALID_ORDERING_CHOICES = {"id": asc(Collection.id), "-id": desc(Collection.id)}

    def __init__(self, session: AsyncSession):
        self.session = session

    async def public_get_collection_repository(self, collection_id: int):
        get_query = select(
            Collection.id,
            Collection.title,
            Collection.image,
        ).where(Collection.id == collection_id)

        get_operation = await self.session.execute(get_query)
        get_result = get_operation.first()

        return get_result

    async def public_get_all_collections_repository(
        self, limit, offset, order_by, search
    ):

        get_all_query = (
            select(
                Collection.id,
                Collection.title,
                Collection.image,
            )
            .limit(limit)
            .offset(offset)
            .order_by(self.VALID_ORDERING_CHOICES.get(order_by))
        )

        if search:
            get_all_query = get_all_query.where(Collection.title.ilike(f"%{search}%"))

        get_all_operation = await self.session.execute(get_all_query)
        get_all_results = get_all_operation.all()

        return get_all_results

    async def get_collection_repository(self, collection_id: int):
        get_query = select(
            Collection.id,
            Collection.title,
            Collection.image,
            Collection.created_at,
            Collection.updated_at,
        ).where(Collection.id == collection_id)

        get_operation = await self.session.execute(get_query)
        get_result = get_operation.first()

        return get_result

    async def count_all_collections(self, search):
        total_collection_query = select(func.count(Collection.id))

        if search:
            total_collection_query = total_collection_query.where(
                Collection.title.ilike(f"%{search}%")
            )

        total_collection_operation = await self.session.execute(total_collection_query)
        total_collection_result = total_collection_operation.first()

        return total_collection_result[0]

    async def valid_order_by(self, order_by):
        return order_by in self.VALID_ORDERING_CHOICES

    async def get_all_collections_repository(self, limit, offset, order_by, search):
        get_all_query = (
            select(
                Collection.id,
                Collection.title,
                Collection.image,
                Collection.created_at,
                Collection.updated_at,
            )
            .limit(limit)
            .offset(offset)
            .order_by(self.VALID_ORDERING_CHOICES.get(order_by))
        )

        if search:
            get_all_query = get_all_query.where(Collection.title.ilike(f"%{search}%"))

        get_all_operation = await self.session.execute(get_all_query)
        get_all_results = get_all_operation.all()

        return get_all_results

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

    async def check_is_unique_title_repository_for_edit(
        self,
        title: str,
        collection_id: int,
    ):
        is_unique_query = select(Collection.id).where(
            and_(Collection.title == title, Collection.id != collection_id)
        )
        is_unique_operation = await self.session.execute(is_unique_query)
        is_unique_result = is_unique_operation.first()

        return is_unique_result

    async def check_is_unique_image_repository_for_update(self, image: str):
        is_unique_query = select(Collection.id).where(Collection.image == image)
        is_unique_operation = await self.session.execute(is_unique_query)
        is_unique_result = is_unique_operation.first()

        return is_unique_result

    async def edit_collection_repository(
        self, payload: EditCollectionRequest, collection_id: int
    ):
        updated_collection_data = payload.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )

        update_collection_query = (
            update(Collection)
            .where(Collection.id == collection_id)
            .values(**updated_collection_data)
        )

        await self.session.execute(update_collection_query)
        await self.session.commit()

    async def delete_collection_repository(self, collection_id: int):
        collection_delete_query = delete(Collection).where(
            Collection.id == collection_id
        )

        await self.session.execute(collection_delete_query)
        await self.session.commit()
