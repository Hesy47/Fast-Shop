from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from application.modules.products.pagination import CustomProductPaginationResponse
from application.modules.products.repository import ProductRepository
from application.modules.products.schemas import (
    CreateProductRequest,
    EditProductRequest,
    GetAllProductsResponse,
    GetProductResponse,
)


class ProductServices:
    def __init__(self, repo: ProductRepository):
        self.repo = repo

    @staticmethod
    def calculate_discount_percent(price: int, discounted_price: int) -> int:
        if price == 0:
            return 0
        return int((price - discounted_price) / price * 100)

    async def get_product_service(self, product_id: int):
        product_repository = await self.repo.get_product_repository(product_id)

        if not product_repository:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="We do not have such this product",
            )

        return GetProductResponse(
            discount_percent=self.calculate_discount_percent(
                product_repository.price,
                product_repository.discounted_price,
            ),
            **product_repository._mapping,
        )

    async def get_all_products_service(
        self,
        page,
        per_page,
        order_by,
        search,
        limit,
        offset,
        base_url,
        route_path,
    ):
        if not await self.repo.valid_order_by(order_by):
            raise HTTPException(
                detail=f"valid order_by choices are: {list(self.repo.VALID_ORDERING_CHOICES.keys())}",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        total_products = await self.repo.count_all_products(search)
        products = await self.repo.get_all_products_repository(
            limit,
            offset,
            order_by,
            search,
        )
        paginated_responses = CustomProductPaginationResponse(
            page,
            per_page,
            limit,
            offset,
            base_url,
            route_path,
            total_products,
        )

        return GetAllProductsResponse(
            count=total_products,
            next=paginated_responses.the_next(),
            previous=paginated_responses.the_previous(),
            total_pages=paginated_responses.total_pages(),
            current_page=page,
            results=[
                GetProductResponse(
                    discount_percent=self.calculate_discount_percent(
                        product.price,
                        product.discounted_price,
                    ),
                    **product._mapping,
                )
                for product in products
            ],
        )

    async def create_product_service(
        self,
        payload: CreateProductRequest,
    ):
        if await self.repo.check_is_unique_title_repository_for_create(payload.title):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "field": "title",
                    "status": status.HTTP_400_BAD_REQUEST,
                    "type": "value_error",
                    "error": "This title is already taken",
                },
            )

        await self._validate_collection_ids(
            payload.collection_id,
            payload.sub_collection_id,
        )

        await self.repo.create_product_repository(payload)

        return JSONResponse(
            content={"message": "New product created successfully"},
            status_code=status.HTTP_201_CREATED,
        )

    async def edit_product_service(
        self,
        product_id: int,
        payload: EditProductRequest,
    ):
        if payload.title and await self.repo.check_is_unique_title_repository_for_edit(
            payload.title,
            product_id,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "field": "title",
                    "status": status.HTTP_400_BAD_REQUEST,
                    "type": "value_error",
                    "error": "This title is already taken",
                },
            )

        await self._validate_collection_ids(
            payload.collection_id,
            payload.sub_collection_id,
        )

        await self.repo.edit_product_repository(payload, product_id)

        return JSONResponse(
            content={"message": "Product updated successfully"},
            status_code=status.HTTP_200_OK,
        )

    async def delete_product_service(self, product_id: int):
        await self.repo.delete_product_repository(product_id)
        return JSONResponse(
            content={"message": "Product has been deleted successfully"},
            status_code=status.HTTP_200_OK,
        )

    async def _validate_collection_ids(
        self,
        collection_id: int | None,
        sub_collection_id: int | None,
    ):
        if collection_id is not None:
            collection_exists = await self.repo.check_collection_existence_repository(
                collection_id
            )
            if not collection_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "field": "collection_id",
                        "status": status.HTTP_400_BAD_REQUEST,
                        "type": "value_error",
                        "error": "This collection does not exist",
                    },
                )

        if sub_collection_id is not None:
            sub_collection_exists = (
                await self.repo.check_sub_collection_existence_repository(
                    sub_collection_id
                )
            )
            if not sub_collection_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "field": "sub_collection_id",
                        "status": status.HTTP_400_BAD_REQUEST,
                        "type": "value_error",
                        "error": "This sub collection does not exist",
                    },
                )
