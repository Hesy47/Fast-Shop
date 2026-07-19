from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Request, UploadFile

from application.core.permissions import CustomPermissions
from application.modules.collections.dependencies import (
    check_collection_existence_by_id_dp,
    collection_services_dp,
)
from application.modules.collections.pagination import CustomCollectionPaginationParams
from application.modules.collections.services import CollectionServices

collection_router = APIRouter(prefix="/api")


@collection_router.get(
    path="/collections/{id:int}",
    tags=["Collection-Public"],
)
async def public_get_collection(
    request: Request,
    id: int,
    service: CollectionServices = Depends(collection_services_dp),
):
    return await service.public_get_collection_service(id, request)


@collection_router.get(
    path="/collections",
    tags=["Collection-Public"],
)
async def public_get_all_collections(
    request: Request,
    params: CustomCollectionPaginationParams = Depends(),
    services: CollectionServices = Depends(
        collection_services_dp,
    ),
):

    return await services.get_all_collections_service(
        params.page,
        params.per_page,
        params.ordering,
        params.search,
        params.limit,
        params.offset,
        request,
        "api/collections",
    )


@collection_router.get(
    path="/get-collection/{collection_id:int}",
    tags=["Collection-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def get_collection(
    request: Request,
    collection_id: int,
    service: CollectionServices = Depends(collection_services_dp),
):
    return await service.get_collection_service(collection_id, request)


@collection_router.get(
    path="/get-all-collections",
    tags=["Collection-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def get_all_collections(
    request: Request,
    params: CustomCollectionPaginationParams = Depends(),
    services: CollectionServices = Depends(
        collection_services_dp,
    ),
):

    return await services.get_all_collections_service(
        params.page,
        params.per_page,
        params.ordering,
        params.search,
        params.limit,
        params.offset,
        request,
        "api/get-all-collections",
    )


@collection_router.post(
    path="/create-collection",
    tags=["Collection-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def create_collection(
    bg: BackgroundTasks,
    title: str = Form(),
    image: UploadFile = File(),
    service: CollectionServices = Depends(collection_services_dp),
):

    return await service.create_collection_service(title, image, bg)


@collection_router.patch(
    path="/edit_collection/{collection_id:int}",
    tags=["Collection-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def edit_collection(
    bg: BackgroundTasks,
    collection_id: int = Depends(check_collection_existence_by_id_dp),
    title: str | None = Form(None),
    image: UploadFile | None = File(None),
    services: CollectionServices = Depends(
        collection_services_dp,
    ),
):
    return await services.edit_collection_service(title, image, collection_id, bg)


@collection_router.delete(
    path="/delete_collection/{collection_id:int}",
    tags=["Collection-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def delete_collection(
    collection_id: int = Depends(check_collection_existence_by_id_dp),
    services: CollectionServices = Depends(
        collection_services_dp,
    ),
):
    return await services.delete_collection_service(collection_id)
