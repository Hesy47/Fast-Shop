from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Request, UploadFile

from application.core.permissions import CustomPermissions
from application.modules.collections.dependencies import collection_services_dp
from application.modules.collections.services import CollectionServices
from application.modules.collections.pagination import CustomCollectionPaginationParams

collection_router = APIRouter(prefix="/api")


@collection_router.get(
    path="/get-collection",
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
