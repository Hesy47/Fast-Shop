from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Request, UploadFile

from application.core.permissions import CustomPermissions
from application.modules.products.dependencies import (
    check_product_existence_by_id_dp,
    check_product_image_existence_by_id_dp,
    check_product_information_existence_by_id_dp,
    product_image_services_dp,
    product_information_services_dp,
    product_services_dp,
)
from application.modules.products.pagination import (
    CustomProductImagePaginationParams,
    CustomProductInformationPaginationParams,
    CustomProductPaginationParams,
)
from application.modules.products.schemas import (
    CreateProductInformationRequest,
    CreateProductRequest,
    EditProductInformationRequest,
    EditProductRequest,
)
from application.modules.products.services import (
    ProductImageServices,
    ProductInformationServices,
    ProductServices,
)

product_router = APIRouter(prefix="/api")


@product_router.get(
    path="/get-product/{product_id:int}",
    tags=["Product-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def get_product(
    product_id: int,
    service: ProductServices = Depends(product_services_dp),
):
    return await service.get_product_service(product_id)


@product_router.get(
    path="/get-all-products",
    tags=["Product-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def get_all_products(
    request: Request,
    params: CustomProductPaginationParams = Depends(),
    service: ProductServices = Depends(product_services_dp),
):
    return await service.get_all_products_service(
        params.page,
        params.per_page,
        params.ordering,
        params.search,
        params.limit,
        params.offset,
        request.base_url,
        "api/get-all-products",
    )


@product_router.post(
    path="/create-product",
    tags=["Product-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def create_product(
    payload: CreateProductRequest,
    service: ProductServices = Depends(product_services_dp),
):
    return await service.create_product_service(payload)


@product_router.patch(
    path="/edit-product/{product_id:int}",
    tags=["Product-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def edit_product(
    payload: EditProductRequest,
    product_id: int = Depends(check_product_existence_by_id_dp),
    service: ProductServices = Depends(product_services_dp),
):
    return await service.edit_product_service(product_id, payload)


@product_router.delete(
    path="/delete-product/{product_id:int}",
    tags=["Product-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def delete_product(
    product_id: int = Depends(check_product_existence_by_id_dp),
    service: ProductServices = Depends(product_services_dp),
):
    return await service.delete_product_service(product_id)


@product_router.get(
    path="/get-product-image/{product_image_id:int}",
    tags=["Product-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def get_product_image(
    request: Request,
    product_image_id: int,
    service: ProductImageServices = Depends(product_image_services_dp),
):
    return await service.get_product_image_service(product_image_id, request)


@product_router.get(
    path="/get-all-product-images",
    tags=["Product-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def get_all_product_images(
    request: Request,
    params: CustomProductImagePaginationParams = Depends(),
    service: ProductImageServices = Depends(product_image_services_dp),
):
    return await service.get_all_product_images_service(
        params.page,
        params.per_page,
        params.ordering,
        params.search,
        params.limit,
        params.offset,
        request,
        "api/get-all-product-images",
    )


@product_router.post(
    path="/create-product-image",
    tags=["Product-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def create_product_image(
    bg: BackgroundTasks,
    product_id: int = Form(),
    image: UploadFile = File(),
    service: ProductImageServices = Depends(product_image_services_dp),
):
    return await service.create_product_image_service(product_id, image, bg)


@product_router.patch(
    path="/edit-product-image/{product_image_id:int}",
    tags=["Product-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def edit_product_image(
    bg: BackgroundTasks,
    product_image_id: int = Depends(check_product_image_existence_by_id_dp),
    product_id: int | None = Form(None),
    image: UploadFile | None = File(None),
    service: ProductImageServices = Depends(product_image_services_dp),
):
    return await service.edit_product_image_service(
        product_image_id,
        product_id,
        image,
        bg,
    )


@product_router.delete(
    path="/delete-product-image/{product_image_id:int}",
    tags=["Product-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def delete_product_image(
    product_image_id: int = Depends(check_product_image_existence_by_id_dp),
    service: ProductImageServices = Depends(product_image_services_dp),
):
    return await service.delete_product_image_service(product_image_id)


@product_router.get(
    path="/get-product-information/{product_information_id:int}",
    tags=["Product-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def get_product_information(
    product_information_id: int,
    service: ProductInformationServices = Depends(product_information_services_dp),
):
    return await service.get_product_information_service(product_information_id)


@product_router.get(
    path="/get-all-product-information",
    tags=["Product-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def get_all_product_information(
    request: Request,
    params: CustomProductInformationPaginationParams = Depends(),
    service: ProductInformationServices = Depends(product_information_services_dp),
):
    return await service.get_all_product_information_service(
        params.page,
        params.per_page,
        params.ordering,
        params.search,
        params.limit,
        params.offset,
        request.base_url,
        "api/get-all-product-information",
    )


@product_router.post(
    path="/create-product-information",
    tags=["Product-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def create_product_information(
    payload: CreateProductInformationRequest,
    service: ProductInformationServices = Depends(product_information_services_dp),
):
    return await service.create_product_information_service(payload)


@product_router.patch(
    path="/edit-product-information/{product_information_id:int}",
    tags=["Product-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def edit_product_information(
    payload: EditProductInformationRequest,
    product_information_id: int = Depends(check_product_information_existence_by_id_dp),
    service: ProductInformationServices = Depends(product_information_services_dp),
):
    return await service.edit_product_information_service(
        product_information_id,
        payload,
    )


@product_router.delete(
    path="/delete-product-information/{product_information_id:int}",
    tags=["Product-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def delete_product_information(
    product_information_id: int = Depends(check_product_information_existence_by_id_dp),
    service: ProductInformationServices = Depends(product_information_services_dp),
):
    return await service.delete_product_information_service(product_information_id)
