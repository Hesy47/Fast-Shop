from fastapi import APIRouter, Depends, Request

from application.core.permissions import CustomPermissions
from application.modules.products.dependencies import (
    check_product_existence_by_id_dp,
    product_services_dp,
)
from application.modules.products.pagination import CustomProductPaginationParams
from application.modules.products.schemas import (
    CreateProductRequest,
    EditProductRequest,
)
from application.modules.products.services import ProductServices

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
