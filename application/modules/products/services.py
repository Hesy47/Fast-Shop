from fastapi import BackgroundTasks, HTTPException, Request, UploadFile, status
from fastapi.responses import JSONResponse

from application.modules.products.pagination import (
    CustomProductImagePaginationResponse,
    CustomProductInformationPaginationResponse,
    CustomProductPaginationResponse,
    PublicProductPaginationResponse,
    SpecialProductPaginationResponse,
)
from application.modules.products.repository import (
    ProductImageRepository,
    ProductInformationRepository,
    ProductRepository,
    PublicProductRepository,
    SpecialProductRepository,
)
from application.modules.products.schemas import (
    CreateProductImageRequest,
    CreateProductInformationRequest,
    CreateProductRequest,
    EditProductImageRequest,
    EditProductInformationRequest,
    EditProductRequest,
    GetAllProductImagesResponse,
    GetAllProductInformationResponse,
    GetAllProductsResponse,
    GetProductImageResponse,
    GetProductInformationResponse,
    GetProductResponse,
    PublicGetAllProductsResponse,
    PublicGetProductResponse,
    SpecialGetAllProductsResponse,
    SpecialGetProductResponse,
)
from application.shared.env_variables import FRONTEND_URL
from application.shared.storage import DiskManager


def build_product_canonical_tag(slug_tag: str | None):
    if slug_tag is None:
        return None
    return f"{FRONTEND_URL.rstrip('/')}/products/{slug_tag}"


class PublicProductServices:
    def __init__(self, repo: PublicProductRepository):
        self.repo = repo

    @staticmethod
    def calculate_discount_percent(price: int, discounted_price: int) -> int:
        if price == 0:
            return 0
        return int((price - discounted_price) / price * 100)

    async def get_product_service(self, product_id: int, request: Request):
        product = await self.repo.get_product_repository(product_id)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="We do not have such this product",
            )

        information, gallery = await self._get_related_data([product.id], request)
        return self._build_product_response(
            product,
            information,
            gallery,
        )

    async def get_all_products_service(
        self,
        page,
        per_page,
        order_by,
        search,
        collection_id,
        sub_collection_id,
        has_discount,
        min_price,
        max_price,
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

        if min_price > max_price:
            raise HTTPException(
                detail="min_price cannot be greater than max_price",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        total_products = await self.repo.count_all_products(
            search,
            collection_id,
            sub_collection_id,
            has_discount,
            min_price,
            max_price,
        )
        products = await self.repo.get_all_products_repository(
            limit,
            offset,
            order_by,
            search,
            collection_id,
            sub_collection_id,
            has_discount,
            min_price,
            max_price,
        )
        product_ids = [product.id for product in products]
        information, gallery = await self._get_related_data(product_ids, request)
        paginated_responses = PublicProductPaginationResponse(
            page,
            per_page,
            limit,
            offset,
            request.base_url,
            route_path,
            total_products,
            request.query_params,
        )

        return PublicGetAllProductsResponse(
            count=total_products,
            next=paginated_responses.the_next(),
            previous=paginated_responses.the_previous(),
            total_pages=paginated_responses.total_pages(),
            current_page=page,
            results=[
                self._build_product_response(
                    product,
                    information,
                    gallery,
                )
                for product in products
            ],
        )

    async def _get_related_data(
        self,
        product_ids: list[int],
        request: Request,
    ):
        product_information = await self.repo.get_product_information_repository(
            product_ids
        )
        product_images = await self.repo.get_product_images_repository(product_ids)

        information_by_product: dict[int, list[dict]] = {
            product_id: [] for product_id in product_ids
        }
        gallery_by_product: dict[int, list[dict]] = {
            product_id: [] for product_id in product_ids
        }

        for information in product_information:
            information_by_product[information.product_id].append(
                {
                    "id": information.id,
                    "key": information.key,
                    "value": information.value,
                }
            )

        for image in product_images:
            gallery_by_product[image.product_id].append(
                {
                    "id": image.id,
                    "image": (
                        f"{request.base_url}"
                        f"{DiskManager.PRODUCTS_SAVE_PATH}"
                        f"{image.image}"
                    ),
                }
            )

        return information_by_product, gallery_by_product

    def _build_product_response(
        self,
        product,
        information_by_product,
        gallery_by_product,
    ):
        return PublicGetProductResponse(
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
            canonical_tag=build_product_canonical_tag(product.slug_tag),
            collection_id=product.collection_id,
            sub_collection_id=product.sub_collection_id,
            product_information=information_by_product.get(product.id, []),
            gallery_set=gallery_by_product.get(product.id, []),
        )


class SpecialProductServices:
    def __init__(self, repo: SpecialProductRepository):
        self.repo = repo

    @staticmethod
    def calculate_discount_percent(price: int, discounted_price: int) -> int:
        if price == 0:
            return 0
        return int((price - discounted_price) / price * 100)

    async def get_product_service(self, product_id: int, request: Request):
        product = await self.repo.get_product_repository(product_id)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="We do not have such this special product",
            )

        return self._build_product_response(product, request)

    async def get_all_products_service(
        self,
        page,
        per_page,
        order_by,
        search,
        collection_id,
        sub_collection_id,
        has_discount,
        min_price,
        max_price,
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

        if min_price > max_price:
            raise HTTPException(
                detail="min_price cannot be greater than max_price",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        filter_arguments = (
            search,
            collection_id,
            sub_collection_id,
            has_discount,
            min_price,
            max_price,
        )
        total_products = await self.repo.count_all_products(*filter_arguments)
        products = await self.repo.get_all_products_repository(
            limit,
            offset,
            order_by,
            *filter_arguments,
        )
        paginated_responses = SpecialProductPaginationResponse(
            page,
            per_page,
            limit,
            offset,
            request.base_url,
            route_path,
            total_products,
            request.query_params,
        )

        return SpecialGetAllProductsResponse(
            count=total_products,
            next=paginated_responses.the_next(),
            previous=paginated_responses.the_previous(),
            total_pages=paginated_responses.total_pages(),
            current_page=page,
            results=[
                self._build_product_response(product, request)
                for product in products
            ],
        )

    def _build_product_response(self, product, request: Request):
        return SpecialGetProductResponse(
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
            canonical_tag=build_product_canonical_tag(product.slug_tag),
            collection_id=product.collection_id,
            sub_collection_id=product.sub_collection_id,
            product_information=[
                {
                    "id": information.id,
                    "key": information.key,
                    "value": information.value,
                }
                for information in sorted(
                    product.information,
                    key=lambda information: information.id,
                )
            ],
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
            canonical_tag=build_product_canonical_tag(
                product_repository.slug_tag
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
                    canonical_tag=build_product_canonical_tag(product.slug_tag),
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

        if await self.repo.check_is_unique_slug_repository_for_create(
            payload.slug_tag
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

        if (
            payload.slug_tag
            and await self.repo.check_is_unique_slug_repository_for_edit(
                payload.slug_tag,
                product_id,
            )
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


class ProductImageServices:
    def __init__(self, repo: ProductImageRepository):
        self.repo = repo

    async def get_product_image_service(
        self,
        product_image_id: int,
        request: Request,
    ):
        product_image = await self.repo.get_product_image_repository(product_image_id)

        if not product_image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="We do not have such this product image",
            )

        return GetProductImageResponse(
            id=product_image.id,
            image=f"{request.base_url}{DiskManager.PRODUCTS_SAVE_PATH}{product_image.image}",
            product_id=product_image.product_id,
            created_at=product_image.created_at,
            updated_at=product_image.updated_at,
        )

    async def get_all_product_images_service(
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

        total_product_images = await self.repo.count_all_product_images(search)
        product_images = await self.repo.get_all_product_images_repository(
            limit,
            offset,
            order_by,
            search,
        )
        paginated_responses = CustomProductImagePaginationResponse(
            page,
            per_page,
            limit,
            offset,
            request.base_url,
            route_path,
            total_product_images,
        )

        return GetAllProductImagesResponse(
            count=total_product_images,
            next=paginated_responses.the_next(),
            previous=paginated_responses.the_previous(),
            total_pages=paginated_responses.total_pages(),
            current_page=page,
            results=[
                {
                    "id": product_image.id,
                    "image": f"{request.base_url}{DiskManager.PRODUCTS_SAVE_PATH}{product_image.image}",
                    "product_id": product_image.product_id,
                    "created_at": product_image.created_at,
                    "updated_at": product_image.updated_at,
                }
                for product_image in product_images
            ],
        )

    async def create_product_image_service(
        self,
        product_id: int,
        image: UploadFile,
        bg: BackgroundTasks,
    ):
        await self._validate_product_id(product_id)
        self._validate_required_image(image)

        image_filename = DiskManager.image_title_webp_convertor_for_route(
            image.filename
        )
        await self._validate_unique_image(image_filename)

        payload = CreateProductImageRequest(
            image=image_filename,
            product_id=product_id,
        )

        await self.repo.create_product_image_repository(payload)
        await self._schedule_image_upload(image, image_filename, bg)

        return JSONResponse(
            content={"message": "New product image created successfully"},
            status_code=status.HTTP_201_CREATED,
        )

    async def edit_product_image_service(
        self,
        product_image_id: int,
        product_id: int | None,
        image: UploadFile | None,
        bg: BackgroundTasks,
    ):
        if product_id is None and (image is None or not image.size):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one field must be provided",
            )

        if product_id is not None:
            await self._validate_product_id(product_id)

        image_filename = None
        if image is not None and image.size:
            image_filename = DiskManager.image_title_webp_convertor_for_route(
                image.filename
            )
            await self._validate_unique_image(
                image_filename,
                product_image_id,
            )

        payload = EditProductImageRequest(
            image=image_filename,
            product_id=product_id,
        )
        await self.repo.edit_product_image_repository(payload, product_image_id)

        if image_filename is not None:
            await self._schedule_image_upload(image, image_filename, bg)

        return JSONResponse(
            content={"message": "Product image updated successfully"},
            status_code=status.HTTP_200_OK,
        )

    async def delete_product_image_service(self, product_image_id: int):
        await self.repo.delete_product_image_repository(product_image_id)
        return JSONResponse(
            content={"message": "Product image has been deleted successfully"},
            status_code=status.HTTP_200_OK,
        )

    async def _validate_product_id(self, product_id: int):
        if not await self.repo.check_product_existence_repository(product_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "field": "product_id",
                    "status": status.HTTP_400_BAD_REQUEST,
                    "type": "value_error",
                    "error": "This product does not exist",
                },
            )

    async def _validate_unique_image(
        self,
        image_filename: str,
        product_image_id: int | None = None,
    ):
        if product_image_id is None:
            image_exists = await self.repo.check_is_unique_image_repository_for_create(
                image_filename
            )
        else:
            image_exists = await self.repo.check_is_unique_image_repository_for_edit(
                image_filename,
                product_image_id,
            )

        if image_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "field": "image",
                    "status": status.HTTP_400_BAD_REQUEST,
                    "type": "value_error",
                    "error": "This image is already taken",
                },
            )

    @staticmethod
    def _validate_required_image(image: UploadFile):
        if not image.size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "field": "image",
                    "status": status.HTTP_400_BAD_REQUEST,
                    "type": "missing",
                    "error": "Field is required",
                },
            )

    @staticmethod
    async def _schedule_image_upload(
        image: UploadFile,
        image_filename: str,
        bg: BackgroundTasks,
    ):
        image_file = await image.read()
        bg.add_task(
            DiskManager.upload_image_for_route,
            DiskManager.image_processor_for_route(image_file, quality=80),
            f"{DiskManager.PRODUCTS_SAVE_PATH}{image_filename}",
        )


class ProductInformationServices:
    def __init__(self, repo: ProductInformationRepository):
        self.repo = repo

    async def get_product_information_service(
        self,
        product_information_id: int,
    ):
        product_information = await self.repo.get_product_information_repository(
            product_information_id
        )

        if not product_information:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="We do not have such this product information",
            )

        return GetProductInformationResponse(**product_information._mapping)

    async def get_all_product_information_service(
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

        total_information = await self.repo.count_all_product_information(search)
        product_information = (
            await self.repo.get_all_product_information_repository(
                limit,
                offset,
                order_by,
                search,
            )
        )
        paginated_responses = CustomProductInformationPaginationResponse(
            page,
            per_page,
            limit,
            offset,
            base_url,
            route_path,
            total_information,
        )

        return GetAllProductInformationResponse(
            count=total_information,
            next=paginated_responses.the_next(),
            previous=paginated_responses.the_previous(),
            total_pages=paginated_responses.total_pages(),
            current_page=page,
            results=[
                GetProductInformationResponse(**information._mapping)
                for information in product_information
            ],
        )

    async def create_product_information_service(
        self,
        payload: CreateProductInformationRequest,
    ):
        await self._validate_product_id(payload.product_id)
        await self._validate_unique_key_and_product(
            payload.key,
            payload.product_id,
        )

        await self.repo.create_product_information_repository(payload)

        return JSONResponse(
            content={"message": "New product information created successfully"},
            status_code=status.HTTP_201_CREATED,
        )

    async def edit_product_information_service(
        self,
        product_information_id: int,
        payload: EditProductInformationRequest,
    ):
        if not payload.model_fields_set:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one field must be provided",
            )

        current_information = await self.repo.get_product_information_repository(
            product_information_id
        )

        effective_key = (
            payload.key if payload.key is not None else current_information.key
        )
        effective_product_id = (
            payload.product_id
            if payload.product_id is not None
            else current_information.product_id
        )

        if payload.product_id is not None:
            await self._validate_product_id(payload.product_id)

        await self._validate_unique_key_and_product(
            effective_key,
            effective_product_id,
            product_information_id,
        )

        await self.repo.edit_product_information_repository(
            payload,
            product_information_id,
        )

        return JSONResponse(
            content={"message": "Product information updated successfully"},
            status_code=status.HTTP_200_OK,
        )

    async def delete_product_information_service(
        self,
        product_information_id: int,
    ):
        await self.repo.delete_product_information_repository(product_information_id)
        return JSONResponse(
            content={"message": "Product information has been deleted successfully"},
            status_code=status.HTTP_200_OK,
        )

    async def _validate_product_id(self, product_id: int):
        if not await self.repo.check_product_existence_repository(product_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "field": "product_id",
                    "status": status.HTTP_400_BAD_REQUEST,
                    "type": "value_error",
                    "error": "This product does not exist",
                },
            )

    async def _validate_unique_key_and_product(
        self,
        key: str,
        product_id: int,
        product_information_id: int | None = None,
    ):
        if product_information_id is None:
            information_exists = (
                await self.repo.check_unique_key_and_product_repository_for_create(
                    key,
                    product_id,
                )
            )
        else:
            information_exists = (
                await self.repo.check_unique_key_and_product_repository_for_edit(
                    key,
                    product_id,
                    product_information_id,
                )
            )

        if information_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "field": "key",
                    "status": status.HTTP_400_BAD_REQUEST,
                    "type": "value_error",
                    "error": "This key is already used for this product",
                },
            )
