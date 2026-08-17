from sqlalchemy import and_, asc, delete, desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from application.modules.sub_collections.models import SubCollection
from application.modules.sub_collections.schemas import (
    CreateSubCollectionRequest,
    EditSubCollectionRequest,
)


class SubCollectionRepository:
    VALID_ORDERING_CHOICES = {
        "id": asc(SubCollection.id),
        "-id": desc(SubCollection.id),
    }

    def __init__(self, session: AsyncSession):
        self.session = session

    async def public_get_sub_collection_repository(self, sub_collection_id: int):
        get_query = select(
            SubCollection.id,
            SubCollection.title,
            SubCollection.image,
            SubCollection.slug_tag,
            SubCollection.title_tag,
            SubCollection.description_tag,
        ).where(SubCollection.id == sub_collection_id)

        get_operation = await self.session.execute(get_query)
        get_result = get_operation.first()

        return get_result

    async def public_get_all_sub_collections_repository(
        self,
        limit,
        offset,
        order_by,
        search,
    ):

        get_all_query = (
            select(
                SubCollection.id,
                SubCollection.title,
                SubCollection.image,
                SubCollection.slug_tag,
                SubCollection.title_tag,
                SubCollection.description_tag,
            )
            .limit(limit)
            .offset(offset)
            .order_by(self.VALID_ORDERING_CHOICES.get(order_by))
        )

        if search:
            get_all_query = get_all_query.where(
                SubCollection.title.ilike(f"%{search}%")
            )

        get_all_operation = await self.session.execute(get_all_query)
        get_all_results = get_all_operation.all()

        return get_all_results

    async def get_sub_collection_repository(self, sub_collection_id: int):
        get_query = select(
            SubCollection.id,
            SubCollection.title,
            SubCollection.image,
            SubCollection.slug_tag,
            SubCollection.title_tag,
            SubCollection.description_tag,
            SubCollection.created_at,
            SubCollection.updated_at,
        ).where(SubCollection.id == sub_collection_id)

        get_operation = await self.session.execute(get_query)
        get_result = get_operation.first()

        return get_result

    async def count_all_sub_collections(self, search):
        total_sub_collection_query = select(func.count(SubCollection.id))

        if search:
            total_sub_collection_query = total_sub_collection_query.where(
                SubCollection.title.ilike(f"%{search}%")
            )

        total_sub_collection_operation = await self.session.execute(
            total_sub_collection_query
        )

        total_sub_collection_result = total_sub_collection_operation.first()

        return total_sub_collection_result[0]

    async def valid_order_by(self, order_by):
        return order_by in self.VALID_ORDERING_CHOICES

    async def get_all_collections_repository(self, limit, offset, order_by, search):
        get_all_query = (
            select(
                SubCollection.id,
                SubCollection.title,
                SubCollection.image,
                SubCollection.slug_tag,
                SubCollection.title_tag,
                SubCollection.description_tag,
                SubCollection.created_at,
                SubCollection.updated_at,
            )
            .limit(limit)
            .offset(offset)
            .order_by(self.VALID_ORDERING_CHOICES.get(order_by))
        )

        if search:
            get_all_query = get_all_query.where(
                SubCollection.title.ilike(f"%{search}%")
            )

        get_all_operation = await self.session.execute(get_all_query)
        get_all_results = get_all_operation.all()

        return get_all_results

    async def check_is_unique_title_repository_for_create(self, title: str):
        is_unique_query = select(SubCollection.id).where(SubCollection.title == title)
        is_unique_operation = await self.session.execute(is_unique_query)
        is_unique_result = is_unique_operation.first()

        return is_unique_result

    async def check_is_unique_image_repository_for_create(self, image: str):
        is_unique_query = select(SubCollection.id).where(SubCollection.image == image)
        is_unique_operation = await self.session.execute(is_unique_query)
        is_unique_result = is_unique_operation.first()

        return is_unique_result

    async def check_is_unique_slug_repository_for_create(self, slug_tag: str):
        is_unique_query = select(SubCollection.id).where(
            SubCollection.slug_tag == slug_tag
        )
        is_unique_operation = await self.session.execute(is_unique_query)
        return is_unique_operation.first()

    async def create_sub_collection_repository(
        self, payload: CreateSubCollectionRequest
    ):
        new_sub_collection = SubCollection(**payload.model_dump())

        self.session.add(new_sub_collection)
        await self.session.commit()

    async def check_is_unique_title_repository_for_edit(
        self,
        title: str,
        sub_collection_id: int,
    ):
        is_unique_query = select(SubCollection.id).where(
            and_(SubCollection.title == title, SubCollection.id != sub_collection_id)
        )
        is_unique_operation = await self.session.execute(is_unique_query)
        is_unique_result = is_unique_operation.first()

        return is_unique_result

    async def check_is_unique_image_repository_for_edit(
        self,
        image: str,
        sub_collection_id: int,
    ):
        is_unique_query = select(SubCollection.id).where(
            and_(
                SubCollection.image == image,
                SubCollection.id != sub_collection_id,
            )
        )
        is_unique_operation = await self.session.execute(is_unique_query)
        is_unique_result = is_unique_operation.first()

        return is_unique_result

    async def check_is_unique_slug_repository_for_edit(
        self,
        slug_tag: str,
        sub_collection_id: int,
    ):
        is_unique_query = select(SubCollection.id).where(
            and_(
                SubCollection.slug_tag == slug_tag,
                SubCollection.id != sub_collection_id,
            )
        )
        is_unique_operation = await self.session.execute(is_unique_query)
        return is_unique_operation.first()

    async def edit_sub_collection_repository(
        self, payload: EditSubCollectionRequest, sub_collection_id: int
    ):
        updated_sub_collection_data = payload.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )

        update_sub_collection_query = (
            update(SubCollection)
            .where(SubCollection.id == sub_collection_id)
            .values(**updated_sub_collection_data)
        )

        await self.session.execute(update_sub_collection_query)
        await self.session.commit()

    async def delete_sub_collection_repository(self, sub_collection_id: int):
        sub_collection_delete_query = delete(SubCollection).where(
            SubCollection.id == sub_collection_id
        )

        await self.session.execute(sub_collection_delete_query)
        await self.session.commit()
