from sqlalchemy import and_, asc, delete, desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, load_only, selectinload

from application.modules.collections.models import Collection
from application.modules.products.models import Product, ProductImage
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
    VALID_PRODUCT_ORDERING_CHOICES = {
        "id": asc(Product.id),
        "-id": desc(Product.id),
        "price": asc(Product.discounted_price),
        "-price": desc(Product.discounted_price),
    }

    def __init__(self, session: AsyncSession):
        self.session = session

    async def public_get_sub_collection_repository(self, slug_tag: str):
        get_query = select(
            SubCollection.id,
            SubCollection.title,
            SubCollection.image,
            SubCollection.slug_tag,
            SubCollection.title_tag,
            SubCollection.description_tag,
        ).where(SubCollection.slug_tag == slug_tag)

        get_operation = await self.session.execute(get_query)
        get_result = get_operation.first()

        return get_result

    @staticmethod
    def _apply_public_product_filters(
        query,
        sub_collection_id: int,
        requested_collection_id: int | None,
        requested_sub_collection_id: int | None,
        has_discount: bool | None,
        min_price: int,
        max_price: int,
        search: str,
    ):
        query = query.where(
            Product.sub_collection_id == sub_collection_id,
            Product.discounted_price.between(min_price, max_price),
        )

        if requested_collection_id is not None:
            query = query.where(Product.collection_id == requested_collection_id)

        if requested_sub_collection_id is not None:
            query = query.where(
                Product.sub_collection_id == requested_sub_collection_id
            )

        if has_discount is True:
            query = query.where(Product.discounted_price < Product.price)
        elif has_discount is False:
            query = query.where(Product.discounted_price >= Product.price)

        if search:
            query = query.where(Product.title.ilike(f"%{search}%"))

        return query

    async def count_public_sub_collection_products(
        self,
        sub_collection_id: int,
        requested_collection_id: int | None,
        requested_sub_collection_id: int | None,
        has_discount: bool | None,
        min_price: int,
        max_price: int,
        search: str,
    ):
        count_query = self._apply_public_product_filters(
            select(func.count(Product.id)),
            sub_collection_id,
            requested_collection_id,
            requested_sub_collection_id,
            has_discount,
            min_price,
            max_price,
            search,
        )
        count_operation = await self.session.execute(count_query)
        return count_operation.scalar_one()

    async def public_get_sub_collection_products_repository(
        self,
        sub_collection_id: int,
        requested_collection_id: int | None,
        requested_sub_collection_id: int | None,
        has_discount: bool | None,
        min_price: int,
        max_price: int,
        search: str,
        order_by: str,
        limit: int,
        offset: int,
    ):
        products_query = self._apply_public_product_filters(
            select(Product),
            sub_collection_id,
            requested_collection_id,
            requested_sub_collection_id,
            has_discount,
            min_price,
            max_price,
            search,
        ).options(
            load_only(
                Product.id,
                Product.title,
                Product.description,
                Product.price,
                Product.discounted_price,
                Product.status,
                Product.menu,
                Product.scroll,
                Product.slug_tag,
                Product.title_tag,
                Product.description_tag,
                Product.collection_id,
                Product.sub_collection_id,
            ),
            joinedload(Product.collection, innerjoin=True).load_only(
                Collection.title
            ),
            selectinload(Product.images).load_only(
                ProductImage.id,
                ProductImage.image,
            ),
        )
        products_query = (
            products_query.order_by(self.VALID_PRODUCT_ORDERING_CHOICES[order_by])
            .limit(limit)
            .offset(offset)
        )

        products_operation = await self.session.execute(products_query)
        return products_operation.scalars().all()

    async def valid_product_order_by(self, order_by: str):
        return order_by in self.VALID_PRODUCT_ORDERING_CHOICES

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
