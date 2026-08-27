from fastapi import APIRouter, Depends, Request

from application.core.permissions import CustomPermissions
from application.modules.scrolls.dependencies import (
    check_scroll_existence_by_id_dp,
    public_scroll_services_dp,
    scroll_services_dp,
)
from application.modules.scrolls.pagination import (
    CustomScrollPaginationParams,
)
from application.modules.scrolls.schemas import (
    CreateScrollRequest,
    EditScrollRequest,
    PublicGetScrollProductsResponse,
)
from application.modules.scrolls.services import PublicScrollServices, ScrollServices

scroll_router = APIRouter(prefix="/api")


@scroll_router.get(
    path="/scroll/{scroll}",
    tags=["Scroll-Public"],
    response_model=PublicGetScrollProductsResponse,
)
async def public_get_scroll_products(
    request: Request,
    scroll: str,
    service: PublicScrollServices = Depends(public_scroll_services_dp),
):
    return await service.get_scroll_products_service(
        scroll,
        request,
    )


@scroll_router.get(
    path="/get-scroll/{scroll_id:int}",
    tags=["Scroll-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def get_scroll(
    scroll_id: int,
    service: ScrollServices = Depends(scroll_services_dp),
):
    return await service.get_scroll_service(scroll_id)


@scroll_router.get(
    path="/get-all-scrolls",
    tags=["Scroll-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def get_all_scrolls(
    request: Request,
    params: CustomScrollPaginationParams = Depends(),
    service: ScrollServices = Depends(scroll_services_dp),
):
    return await service.get_all_scrolls_service(
        params.page,
        params.per_page,
        params.ordering,
        params.search,
        params.limit,
        params.offset,
        request,
        "api/get-all-scrolls",
    )


@scroll_router.post(
    path="/create-scroll",
    tags=["Scroll-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def create_scroll(
    payload: CreateScrollRequest,
    service: ScrollServices = Depends(scroll_services_dp),
):
    return await service.create_scroll_service(payload)


@scroll_router.patch(
    path="/edit-scroll/{scroll_id:int}",
    tags=["Scroll-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def edit_scroll(
    payload: EditScrollRequest,
    scroll_id: int = Depends(check_scroll_existence_by_id_dp),
    service: ScrollServices = Depends(scroll_services_dp),
):
    return await service.edit_scroll_service(scroll_id, payload)


@scroll_router.delete(
    path="/delete-scroll/{scroll_id:int}",
    tags=["Scroll-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def delete_scroll(
    scroll_id: int = Depends(check_scroll_existence_by_id_dp),
    service: ScrollServices = Depends(scroll_services_dp),
):
    return await service.delete_scroll_service(scroll_id)
