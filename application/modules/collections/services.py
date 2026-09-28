from fastapi import BackgroundTasks, File, HTTPException, Request, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from application.modules.collections.pagination import (
    CustomCollectionPaginationResponse,
    PublicCollectionProductPaginationResponse,
)
from application.modules.collections.repository import CollectionRepository
from application.modules.collections.schemas import (
    CreateCollectionRequest,
    EditCollectionRequest,
    GetAllCollectionsResponse,
    GetCollectionResponse,
    PublicGetAllCollectionsResponse,
    PublicCollectionProductResponse,
    PublicGetCollectionResponse,
)
from application.shared.env_variables import FRONTEND_URL
from application.shared.exceptions import CustomExceptionsHandlers
from application.shared.storage import DiskManager


class CollectionServices:
    def __init__(self, repo: CollectionRepository):
        self.repo = repo

    @staticmethod
    def build_canonical_tag(request: Request, slug_tag: str | None):
        if slug_tag is None:
            return None
        return f"{FRONTEND_URL}/collections/{slug_tag}"

    @staticmethod
    def build_product_canonical_tag(slug_tag: str | None):
        if slug_tag is None:
            return None
        return f"{FRONTEND_URL.rstrip('/')}/products/{slug_tag}"

    @staticmethod
    def calculate_discount_percent(price: int, discounted_price: int) -> str:
        if price == 0:
            return "0 %"
        discount_percent = int((price - discounted_price) / price * 100)
        return f"{discount_percent} %"

    async def public_get_collection_service(
        self,
        slug_tag: str,
        page: int,
        per_page: int,
        order_by: str,
        search: str,
        requested_collection_id: int | None,
        sub_collection_id: int | None,
        has_discount: bool | None,
        min_price: int,
        max_price: int,
        limit: int,
        offset: int,
        request: Request,
        route_path: str,
    ):
        collection_repository = await self.repo.public_get_collection_repository(
            slug_tag
        )

        if not collection_repository:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="We do not have such this collection",
            )

        if not await self.repo.valid_product_order_by(order_by):
            raise HTTPException(
                detail=(
                    "valid order_by choices are: "
                    f"{list(self.repo.VALID_PRODUCT_ORDERING_CHOICES.keys())}"
                ),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if min_price > max_price:
            raise HTTPException(
                detail="min_price cannot be greater than max_price",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        product_filter_arguments = (
            collection_repository.id,
            requested_collection_id,
            sub_collection_id,
            has_discount,
            min_price,
            max_price,
            search,
        )
        total_products = await self.repo.count_public_collection_products(
            *product_filter_arguments
        )
        products = await self.repo.public_get_collection_products_repository(
            *product_filter_arguments,
            order_by,
            limit,
            offset,
        )
        pagination = PublicCollectionProductPaginationResponse(
            page,
            per_page,
            limit,
            offset,
            request.base_url,
            route_path,
            total_products,
            request.query_params,
        )

        return PublicGetCollectionResponse(
            id=collection_repository.id,
            title=collection_repository.title,
            image=f"{request.base_url}{DiskManager.COLLECTIONS_SAVE_PATH}{collection_repository.image}",
            slug_tag=collection_repository.slug_tag,
            title_tag=collection_repository.title_tag,
            description_tag=collection_repository.description_tag,
            canonical_tag=self.build_canonical_tag(
                request,
                collection_repository.slug_tag,
            ),
            count=total_products,
            next=pagination.the_next(),
            previous=pagination.the_previous(),
            total_pages=pagination.total_pages(),
            current_page=page,
            results=[
                self._build_public_collection_product_response(
                    product,
                    collection_repository.title,
                    request,
                )
                for product in products
            ],
        )

    def _build_public_collection_product_response(
        self,
        product,
        collection_title: str,
        request: Request,
    ):
        return PublicCollectionProductResponse(
            id=product.id,
            title=product.title,
            description=product.description,
            price=product.price,
            discounted_price=product.discounted_price,
            discount_percent=self.calculate_discount_percent(
                product.price,
                product.discounted_price,
            ),
            status=product.status,
            menu=product.menu,
            scroll=product.scroll,
            slug_tag=product.slug_tag,
            title_tag=product.title_tag,
            description_tag=product.description_tag,
            canonical_tag=self.build_product_canonical_tag(product.slug_tag),
            collection_id=product.collection_id,
            collection_title=collection_title,
            sub_collection_id=product.sub_collection_id,
            sub_collection_title=(
                product.sub_collection.title
                if product.sub_collection is not None
                else None
            ),
            gallery_set=[
                {
                    "id": image.id,
                    "image": (
                        f"{request.base_url}"
                        f"{DiskManager.PRODUCTS_SAVE_PATH}"
                        f"{image.image}"
                    ),
                }
                for image in sorted(product.images, key=lambda image: image.id)
            ],
        )

    async def public_get_all_collections_service(
        self,
        page,
        per_page,
        order_by,
        search,
        limit,
        offset,
        request: Request,
        route_path,
    ):
        if per_page > 20:
            raise HTTPException(
                detail="maximum item per page is 20",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if not await self.repo.valid_order_by(order_by):
            raise HTTPException(
                detail=f"valid order_by choices are: {list(self.repo.VALID_ORDERING_CHOICES.keys())}",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        total_collection_repository = await self.repo.count_all_collections(search)
        collection_repository = await self.repo.public_get_all_collections_repository(
            limit, offset, order_by, search
        )
        paginated_responses = CustomCollectionPaginationResponse(
            page,
            per_page,
            limit,
            offset,
            request.base_url,
            route_path,
            total_collection_repository,
        )

        return PublicGetAllCollectionsResponse(
            count=total_collection_repository,
            next=paginated_responses.the_next(),
            previous=paginated_responses.the_previous(),
            total_pages=paginated_responses.total_pages(),
            current_page=page,
            results=[
                {
                    "id": collection.id,
                    "title": collection.title,
                    "image": f"{request.base_url}{DiskManager.COLLECTIONS_SAVE_PATH}{collection.image}",
                    "slug_tag": collection.slug_tag,
                    "title_tag": collection.title_tag,
                    "description_tag": collection.description_tag,
                    "canonical_tag": self.build_canonical_tag(
                        request,
                        collection.slug_tag,
                    ),
                }
                for collection in collection_repository
            ],
        )

    async def get_collection_service(self, collection_id: int, request: Request):
        collection_repository = await self.repo.get_collection_repository(collection_id)

        if not collection_repository:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="We do not have such this collection",
            )

        return GetCollectionResponse(
            id=collection_repository.id,
            title=collection_repository.title,
            image=f"{request.base_url}{DiskManager.COLLECTIONS_SAVE_PATH}{collection_repository.image}",
            slug_tag=collection_repository.slug_tag,
            title_tag=collection_repository.title_tag,
            description_tag=collection_repository.description_tag,
            canonical_tag=self.build_canonical_tag(
                request,
                collection_repository.slug_tag,
            ),
            created_at=collection_repository.created_at,
            updated_at=collection_repository.updated_at,
        )

    async def get_all_collections_service(
        self,
        page,
        per_page,
        order_by,
        search,
        limit,
        offset,
        request: Request,
        route_path,
    ):
        if not await self.repo.valid_order_by(order_by):
            raise HTTPException(
                detail=f"valid order_by choices are: {list(self.repo.VALID_ORDERING_CHOICES.keys())}",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        total_collection_repository = await self.repo.count_all_collections(search)
        collection_repository = await self.repo.get_all_collections_repository(
            limit, offset, order_by, search
        )
        paginated_responses = CustomCollectionPaginationResponse(
            page,
            per_page,
            limit,
            offset,
            request.base_url,
            route_path,
            total_collection_repository,
        )

        return GetAllCollectionsResponse(
            count=total_collection_repository,
            next=paginated_responses.the_next(),
            previous=paginated_responses.the_previous(),
            total_pages=paginated_responses.total_pages(),
            current_page=page,
            results=[
                {
                    "id": collection.id,
                    "title": collection.title,
                    "image": f"{request.base_url}{DiskManager.COLLECTIONS_SAVE_PATH}{collection.image}",
                    "slug_tag": collection.slug_tag,
                    "title_tag": collection.title_tag,
                    "description_tag": collection.description_tag,
                    "canonical_tag": self.build_canonical_tag(
                        request,
                        collection.slug_tag,
                    ),
                    "created_at": collection.created_at,
                    "updated_at": collection.updated_at,
                }
                for collection in collection_repository
            ],
        )

    async def create_collection_service(
        self,
        title: str,
        image: UploadFile,
        slug_tag: str,
        title_tag: str | None,
        description_tag: str | None,
        bg: BackgroundTasks,
    ):
        if not int(image.size) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "field": "image",
                    "status": status.HTTP_400_BAD_REQUEST,
                    "type": "missing",
                    "error": "Field is required",
                },
            )

        if await self.repo.check_is_unique_title_repository_for_create(title):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "field": "title",
                    "status": status.HTTP_400_BAD_REQUEST,
                    "type": "value_error",
                    "error": "This title is already taken",
                },
            )

        if await self.repo.check_is_unique_slug_repository_for_create(slug_tag):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "field": "slug_tag",
                    "status": status.HTTP_400_BAD_REQUEST,
                    "type": "value_error",
                    "error": "This slug is already taken",
                },
            )

        image_filename = DiskManager.image_title_webp_convertor_for_route(
            image.filename
        )

        if await self.repo.check_is_unique_image_repository_for_create(image_filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "field": "image",
                    "status": status.HTTP_400_BAD_REQUEST,
                    "type": "value_error",
                    "error": "This image is already taken",
                },
            )

        try:
            payload = CreateCollectionRequest(
                title=title,
                image=image_filename,
                slug_tag=slug_tag,
                title_tag=title_tag,
                description_tag=description_tag,
            )
        except ValidationError as error:
            await CustomExceptionsHandlers.pydantic_validation_handler_for_route(error)

        await self.repo.create_collection_repository(payload)

        image_file = await image.read()

        bg.add_task(
            DiskManager.upload_image_for_route,
            DiskManager.image_processor_for_route(image_file, quality=85),
            f"{DiskManager.COLLECTIONS_SAVE_PATH}{image_filename}",
        )

        return JSONResponse(
            content={"message": "New collection created successfully"},
            status_code=status.HTTP_201_CREATED,
        )

    async def edit_collection_service(
        self,
        title: str,
        image: UploadFile | None,
        slug_tag: str | None,
        title_tag: str | None,
        description_tag: str | None,
        collection_id: int,
        bg: BackgroundTasks,
    ):
        if title:
            if await self.repo.check_is_unique_title_repository_for_edit(
                title,
                collection_id,
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

        if slug_tag and await self.repo.check_is_unique_slug_repository_for_edit(
            slug_tag,
            collection_id,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "field": "slug_tag",
                    "status": status.HTTP_400_BAD_REQUEST,
                    "type": "value_error",
                    "error": "This slug is already taken",
                },
            )

        has_image = image is not None and bool(image.size)
        if has_image:
            image_filename = DiskManager.image_title_webp_convertor_for_route(
                image.filename
            )

            if await self.repo.check_is_unique_image_repository_for_update(
                image_filename,
                collection_id,
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "field": "image",
                        "status": status.HTTP_400_BAD_REQUEST,
                        "type": "value_error",
                        "error": "This image is already taken",
                    },
                )
        else:
            image_filename = None

        try:
            payload = EditCollectionRequest(
                title=title,
                image=image_filename,
                slug_tag=slug_tag,
                title_tag=title_tag,
                description_tag=description_tag,
            )
        except ValidationError as error:
            await CustomExceptionsHandlers.pydantic_validation_handler_for_route(error)

        await self.repo.edit_collection_repository(payload, collection_id)

        if has_image:
            image_file = await image.read()

            bg.add_task(
                DiskManager.upload_image_for_route,
                DiskManager.image_processor_for_route(image_file, quality=85),
                f"{DiskManager.COLLECTIONS_SAVE_PATH}{image_filename}",
            )

        return JSONResponse(
            content={"message": "collection updated successfully"},
            status_code=status.HTTP_200_OK,
        )

    async def delete_collection_service(self, collection_id: int):
        await self.repo.delete_collection_repository(collection_id)
        return JSONResponse(
            content={"message": "Collection has been deleted successfully"},
            status_code=status.HTTP_200_OK,
        )
