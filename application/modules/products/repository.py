from sqlalchemy import and_, asc, delete, desc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, load_only, selectinload

from application.modules.collections.models import Collection
from application.modules.products.models import (
    MenuType,
    Product,
    ProductImage,
    ProductInformation,
)
from application.modules.products.schemas import (
    CreateProductImageRequest,
    CreateProductInformationRequest,
    CreateProductRequest,
    EditProductImageRequest,
    EditProductInformationRequest,
    EditProductRequest,
)
from application.modules.sub_collections.models import SubCollection


class PublicProductRepository:
    VALID_ORDERING_CHOICES = {
        "id": asc(Product.id),
        "-id": desc(Product.id),
    }

    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _product_columns():
        return (
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
        )

    @classmethod
    def _select_with_collection_titles(cls):
        return (
            select(
                *cls._product_columns(),
                Collection.title.label("collection_title"),
                SubCollection.title.label("sub_collection_title"),
            )
            .join(Collection, Product.collection_id == Collection.id)
            .outerjoin(
                SubCollection,
                Product.sub_collection_id == SubCollection.id,
            )
        )

    async def get_product_repository(self, product_id: int):
        get_query = self._select_with_collection_titles().where(
            and_(Product.id == product_id, Product.menu == MenuType.casual)
        )

        get_operation = await self.session.execute(get_query)
        return get_operation.first()

    async def get_product_images_repository(self, product_ids: list[int]):
        if not product_ids:
            return []

        images_query = (
            select(
                ProductImage.id,
                ProductImage.image,
                ProductImage.product_id,
            )
            .where(ProductImage.product_id.in_(product_ids))
            .order_by(ProductImage.id)
        )

        images_operation = await self.session.execute(images_query)
        return images_operation.all()

    async def get_product_information_repository(self, product_ids: list[int]):
        if not product_ids:
            return []

        information_query = (
            select(
                ProductInformation.id,
                ProductInformation.key,
                ProductInformation.value,
                ProductInformation.product_id,
            )
            .where(ProductInformation.product_id.in_(product_ids))
            .order_by(ProductInformation.id)
        )

        information_operation = await self.session.execute(information_query)
        return information_operation.all()

    @staticmethod
    def _apply_filters(
        query,
        search: str,
        collection_id: int | None,
        sub_collection_id: int | None,
        has_discount: bool | None,
        min_price: int,
        max_price: int,
    ):
        query = query.where(Product.discounted_price.between(min_price, max_price))

        if search:
            query = query.where(Product.title.ilike(f"%{search}%"))

        if collection_id is not None:
            query = query.where(Product.collection_id == collection_id)

        if sub_collection_id is not None:
            query = query.where(Product.sub_collection_id == sub_collection_id)

        if has_discount is True:
            query = query.where(Product.discounted_price < Product.price)
        elif has_discount is False:
            query = query.where(Product.discounted_price >= Product.price)

        return query

    async def count_all_products(
        self,
        search: str,
        collection_id: int | None,
        sub_collection_id: int | None,
        has_discount: bool | None,
        min_price: int,
        max_price: int,
    ):
        count_query = select(func.count(Product.id))
        count_query = self._apply_filters(
            count_query,
            search,
            collection_id,
            sub_collection_id,
            has_discount,
            min_price,
            max_price,
        )

        count_operation = await self.session.execute(count_query)
        return count_operation.scalar_one()

    async def valid_order_by(self, order_by: str):
        return order_by in self.VALID_ORDERING_CHOICES

    async def get_all_products_repository(
        self,
        limit: int,
        offset: int,
        order_by: str,
        search: str,
        collection_id: int | None,
        sub_collection_id: int | None,
        has_discount: bool | None,
        min_price: int,
        max_price: int,
    ):
        get_all_query = self._select_with_collection_titles()
        get_all_query = self._apply_filters(
            get_all_query,
            search,
            collection_id,
            sub_collection_id,
            has_discount,
            min_price,
            max_price,
        )
        get_all_query = (
            get_all_query.limit(limit)
            .offset(offset)
            .order_by(self.VALID_ORDERING_CHOICES[order_by])
            .where(Product.menu == "casual")
        )

        get_all_operation = await self.session.execute(get_all_query)
        return get_all_operation.all()


class SpecialProductRepository:
    VALID_ORDERING_CHOICES = {
        "id": asc(Product.id),
        "-id": desc(Product.id),
    }

    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _with_filters(
        query,
        search: str,
        collection_id: int | None,
        sub_collection_id: int | None,
        has_discount: bool | None,
        min_price: int,
        max_price: int,
    ):
        query = PublicProductRepository._apply_filters(
            query,
            search,
            collection_id,
            sub_collection_id,
            has_discount,
            min_price,
            max_price,
        )
        return query.where(Product.menu == MenuType.special)

    @staticmethod
    def _with_related_data(query):
        return query.options(
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
                Collection.title,
            ),
            joinedload(Product.sub_collection).load_only(
                SubCollection.title,
            ),
            selectinload(Product.images).load_only(
                ProductImage.id,
                ProductImage.image,
            ),
            selectinload(Product.information).load_only(
                ProductInformation.id,
                ProductInformation.key,
                ProductInformation.value,
            ),
        )

    async def get_product_repository(self, product_id: int):
        get_query = self._with_related_data(
            select(Product).where(
                Product.id == product_id,
                Product.menu == MenuType.special,
            )
        )

        get_operation = await self.session.execute(get_query)
        return get_operation.scalar_one_or_none()

    async def count_all_products(
        self,
        search: str,
        collection_id: int | None,
        sub_collection_id: int | None,
        has_discount: bool | None,
        min_price: int,
        max_price: int,
    ):
        count_query = self._with_filters(
            select(func.count(Product.id)),
            search,
            collection_id,
            sub_collection_id,
            has_discount,
            min_price,
            max_price,
        )

        count_operation = await self.session.execute(count_query)
        return count_operation.scalar_one()

    async def valid_order_by(self, order_by: str):
        return order_by in self.VALID_ORDERING_CHOICES

    async def get_all_products_repository(
        self,
        limit: int,
        offset: int,
        order_by: str,
        search: str,
        collection_id: int | None,
        sub_collection_id: int | None,
        has_discount: bool | None,
        min_price: int,
        max_price: int,
    ):
        get_all_query = self._with_related_data(
            self._with_filters(
                select(Product),
                search,
                collection_id,
                sub_collection_id,
                has_discount,
                min_price,
                max_price,
            )
            .limit(limit)
            .offset(offset)
            .order_by(self.VALID_ORDERING_CHOICES[order_by])
        )

        get_all_operation = await self.session.execute(get_all_query)
        return get_all_operation.scalars().all()


class ProductRepository:
    VALID_ORDERING_CHOICES = {
        "id": asc(Product.id),
        "-id": desc(Product.id),
    }

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_product_repository(self, product_id: int):
        get_query = select(
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
            Product.created_at,
            Product.updated_at,
        ).where(Product.id == product_id)

        get_operation = await self.session.execute(get_query)
        return get_operation.first()

    async def count_all_products(self, search: str):
        count_query = select(func.count(Product.id))

        if search:
            count_query = count_query.where(Product.title.ilike(f"%{search}%"))

        count_operation = await self.session.execute(count_query)
        return count_operation.scalar_one()

    async def valid_order_by(self, order_by: str):
        return order_by in self.VALID_ORDERING_CHOICES

    async def get_all_products_repository(
        self,
        limit: int,
        offset: int,
        order_by: str,
        search: str,
    ):
        get_all_query = (
            select(
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
                Product.created_at,
                Product.updated_at,
            )
            .limit(limit)
            .offset(offset)
            .order_by(self.VALID_ORDERING_CHOICES[order_by])
        )

        if search:
            get_all_query = get_all_query.where(Product.title.ilike(f"%{search}%"))

        get_all_operation = await self.session.execute(get_all_query)
        return get_all_operation.all()

    async def check_is_unique_title_repository_for_create(self, title: str):
        unique_query = select(Product.id).where(Product.title == title)
        unique_operation = await self.session.execute(unique_query)
        return unique_operation.first()

    async def check_is_unique_slug_repository_for_create(self, slug_tag: str):
        unique_query = select(Product.id).where(Product.slug_tag == slug_tag)
        unique_operation = await self.session.execute(unique_query)
        return unique_operation.first()

    async def check_collection_existence_repository(self, collection_id: int):
        collection_query = select(Collection.id).where(Collection.id == collection_id)
        collection_operation = await self.session.execute(collection_query)
        return collection_operation.first()

    async def check_sub_collection_existence_repository(
        self,
        sub_collection_id: int,
    ):
        sub_collection_query = select(SubCollection.id).where(
            SubCollection.id == sub_collection_id
        )
        sub_collection_operation = await self.session.execute(sub_collection_query)
        return sub_collection_operation.first()

    async def create_product_repository(self, payload: CreateProductRequest):
        new_product = Product(**payload.model_dump())

        self.session.add(new_product)
        await self.session.commit()

    async def check_is_unique_title_repository_for_edit(
        self,
        title: str,
        product_id: int,
    ):
        unique_query = select(Product.id).where(
            and_(Product.title == title, Product.id != product_id)
        )
        unique_operation = await self.session.execute(unique_query)
        return unique_operation.first()

    async def check_is_unique_slug_repository_for_edit(
        self,
        slug_tag: str,
        product_id: int,
    ):
        unique_query = select(Product.id).where(
            and_(Product.slug_tag == slug_tag, Product.id != product_id)
        )
        unique_operation = await self.session.execute(unique_query)
        return unique_operation.first()

    async def edit_product_repository(
        self,
        payload: EditProductRequest,
        product_id: int,
    ):
        updated_product_data = payload.model_dump(
            exclude_unset=True,
        )

        update_query = (
            update(Product)
            .where(Product.id == product_id)
            .values(**updated_product_data)
        )

        await self.session.execute(update_query)
        await self.session.commit()

    async def delete_product_repository(self, product_id: int):
        delete_query = delete(Product).where(Product.id == product_id)

        await self.session.execute(delete_query)
        await self.session.commit()


class ProductImageRepository:
    VALID_ORDERING_CHOICES = {
        "id": asc(ProductImage.id),
        "-id": desc(ProductImage.id),
    }

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_product_image_repository(self, product_image_id: int):
        get_query = select(
            ProductImage.id,
            ProductImage.image,
            ProductImage.product_id,
            ProductImage.created_at,
            ProductImage.updated_at,
        ).where(ProductImage.id == product_image_id)

        get_operation = await self.session.execute(get_query)
        return get_operation.first()

    async def count_all_product_images(self, search: str):
        count_query = select(func.count(ProductImage.id))

        if search:
            count_query = count_query.where(ProductImage.image.ilike(f"%{search}%"))

        count_operation = await self.session.execute(count_query)
        return count_operation.scalar_one()

    async def valid_order_by(self, order_by: str):
        return order_by in self.VALID_ORDERING_CHOICES

    async def get_all_product_images_repository(
        self,
        limit: int,
        offset: int,
        order_by: str,
        search: str,
    ):
        get_all_query = (
            select(
                ProductImage.id,
                ProductImage.image,
                ProductImage.product_id,
                ProductImage.created_at,
                ProductImage.updated_at,
            )
            .limit(limit)
            .offset(offset)
            .order_by(self.VALID_ORDERING_CHOICES[order_by])
        )

        if search:
            get_all_query = get_all_query.where(ProductImage.image.ilike(f"%{search}%"))

        get_all_operation = await self.session.execute(get_all_query)
        return get_all_operation.all()

    async def check_product_existence_repository(self, product_id: int):
        product_query = select(Product.id).where(Product.id == product_id)
        product_operation = await self.session.execute(product_query)
        return product_operation.first()

    async def check_is_unique_image_repository_for_create(self, image: str):
        unique_query = select(ProductImage.id).where(ProductImage.image == image)
        unique_operation = await self.session.execute(unique_query)
        return unique_operation.first()

    async def check_is_unique_image_repository_for_edit(
        self,
        image: str,
        product_image_id: int,
    ):
        unique_query = select(ProductImage.id).where(
            and_(
                ProductImage.image == image,
                ProductImage.id != product_image_id,
            )
        )
        unique_operation = await self.session.execute(unique_query)
        return unique_operation.first()

    async def create_product_image_repository(
        self,
        payload: CreateProductImageRequest,
    ):
        new_product_image = ProductImage(**payload.model_dump())

        self.session.add(new_product_image)
        await self.session.commit()

    async def edit_product_image_repository(
        self,
        payload: EditProductImageRequest,
        product_image_id: int,
    ):
        updated_product_image_data = payload.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )

        update_query = (
            update(ProductImage)
            .where(ProductImage.id == product_image_id)
            .values(**updated_product_image_data)
        )

        await self.session.execute(update_query)
        await self.session.commit()

    async def delete_product_image_repository(self, product_image_id: int):
        delete_query = delete(ProductImage).where(ProductImage.id == product_image_id)

        await self.session.execute(delete_query)
        await self.session.commit()


class ProductInformationRepository:
    VALID_ORDERING_CHOICES = {
        "id": asc(ProductInformation.id),
        "-id": desc(ProductInformation.id),
    }

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_product_information_repository(
        self,
        product_information_id: int,
    ):
        get_query = select(
            ProductInformation.id,
            ProductInformation.key,
            ProductInformation.value,
            ProductInformation.product_id,
            ProductInformation.created_at,
            ProductInformation.updated_at,
        ).where(ProductInformation.id == product_information_id)

        get_operation = await self.session.execute(get_query)
        return get_operation.first()

    async def count_all_product_information(self, search: str):
        count_query = select(func.count(ProductInformation.id))

        if search:
            count_query = count_query.where(
                or_(
                    ProductInformation.key.ilike(f"%{search}%"),
                    ProductInformation.value.ilike(f"%{search}%"),
                )
            )

        count_operation = await self.session.execute(count_query)
        return count_operation.scalar_one()

    async def valid_order_by(self, order_by: str):
        return order_by in self.VALID_ORDERING_CHOICES

    async def get_all_product_information_repository(
        self,
        limit: int,
        offset: int,
        order_by: str,
        search: str,
    ):
        get_all_query = (
            select(
                ProductInformation.id,
                ProductInformation.key,
                ProductInformation.value,
                ProductInformation.product_id,
                ProductInformation.created_at,
                ProductInformation.updated_at,
            )
            .limit(limit)
            .offset(offset)
            .order_by(self.VALID_ORDERING_CHOICES[order_by])
        )

        if search:
            get_all_query = get_all_query.where(
                or_(
                    ProductInformation.key.ilike(f"%{search}%"),
                    ProductInformation.value.ilike(f"%{search}%"),
                )
            )

        get_all_operation = await self.session.execute(get_all_query)
        return get_all_operation.all()

    async def check_product_existence_repository(self, product_id: int):
        product_query = select(Product.id).where(Product.id == product_id)
        product_operation = await self.session.execute(product_query)
        return product_operation.first()

    async def check_unique_key_and_product_repository_for_create(
        self,
        key: str,
        product_id: int,
    ):
        unique_query = select(ProductInformation.id).where(
            and_(
                ProductInformation.key == key,
                ProductInformation.product_id == product_id,
            )
        )
        unique_operation = await self.session.execute(unique_query)
        return unique_operation.first()

    async def check_unique_key_and_product_repository_for_edit(
        self,
        key: str,
        product_id: int,
        product_information_id: int,
    ):
        unique_query = select(ProductInformation.id).where(
            and_(
                ProductInformation.key == key,
                ProductInformation.product_id == product_id,
                ProductInformation.id != product_information_id,
            )
        )
        unique_operation = await self.session.execute(unique_query)
        return unique_operation.first()

    async def create_product_information_repository(
        self,
        payload: CreateProductInformationRequest,
    ):
        new_product_information = ProductInformation(**payload.model_dump())

        self.session.add(new_product_information)
        await self.session.commit()

    async def edit_product_information_repository(
        self,
        payload: EditProductInformationRequest,
        product_information_id: int,
    ):
        updated_information_data = payload.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )

        update_query = (
            update(ProductInformation)
            .where(ProductInformation.id == product_information_id)
            .values(**updated_information_data)
        )

        await self.session.execute(update_query)
        await self.session.commit()

    async def delete_product_information_repository(
        self,
        product_information_id: int,
    ):
        delete_query = delete(ProductInformation).where(
            ProductInformation.id == product_information_id
        )

        await self.session.execute(delete_query)
        await self.session.commit()
