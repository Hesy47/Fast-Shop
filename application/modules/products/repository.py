from sqlalchemy import and_, asc, delete, desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from application.modules.collections.models import Collection
from application.modules.products.models import Product, ProductImage
from application.modules.products.schemas import (
    CreateProductImageRequest,
    CreateProductRequest,
    EditProductImageRequest,
    EditProductRequest,
)
from application.modules.sub_collections.models import SubCollection


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
