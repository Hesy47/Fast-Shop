from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Request, UploadFile

from application.core.permissions import CustomPermissions
from application.modules.sub_collections.dependencies import (
    check_sub_collection_existence_by_id_dp,
    sub_collection_services_dp,
)
from application.modules.sub_collections.pagination import (
    CustomSubCollectionPaginationParams,
)
from application.modules.sub_collections.services import SubCollectionServices

sub_collection_router = APIRouter(prefix="/api")


@sub_collection_router.get(
    path="/sub-collections/{slug_tag}",
    tags=["Sub-Collection-Public"],
)
async def public_get_sub_collection(
    request: Request,
    slug_tag: str,
    service: SubCollectionServices = Depends(sub_collection_services_dp),
):
    return await service.public_get_sub_collection_service(
        slug_tag,
        request,
    )


@sub_collection_router.get(
    path="/sub-collections",
    tags=["Sub-Collection-Public"],
)
async def public_get_all_sub_collections(
    request: Request,
    params: CustomSubCollectionPaginationParams = Depends(),
    services: SubCollectionServices = Depends(
        sub_collection_services_dp,
    ),
):

    return await services.public_get_all_sub_collections_service(
        params.page,
        params.per_page,
        params.ordering,
        params.search,
        params.limit,
        params.offset,
        request,
        "api/sub-collections",
    )


@sub_collection_router.get(
    path="/get-sub-collection/{sub_collection_id:int}",
    tags=["Sub-Collection-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def get_sub_collection(
    request: Request,
    sub_collection_id: int,
    service: SubCollectionServices = Depends(sub_collection_services_dp),
):
    return await service.get_sub_collection_service(sub_collection_id, request)


@sub_collection_router.get(
    path="/get-all-sub-collections",
    tags=["Sub-Collection-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def get_all_sub_collections(
    request: Request,
    params: CustomSubCollectionPaginationParams = Depends(),
    services: SubCollectionServices = Depends(
        sub_collection_services_dp,
    ),
):

    return await services.get_all_sub_collections_service(
        params.page,
        params.per_page,
        params.ordering,
        params.search,
        params.limit,
        params.offset,
        request,
        "api/get-all-collections",
    )


@sub_collection_router.post(
    path="/create-sub-collection",
    tags=["Sub-Collection-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def create_sub_collection(
    bg: BackgroundTasks,
    title: str = Form(),
    image: UploadFile = File(),
    slug_tag: str = Form(),
    title_tag: str | None = Form(None),
    description_tag: str | None = Form(None),
    service: SubCollectionServices = Depends(sub_collection_services_dp),
):

    return await service.create_sub_collection_service(
        title,
        image,
        slug_tag,
        title_tag,
        description_tag,
        bg,
    )


@sub_collection_router.patch(
    path="/edit-sub-collection/{sub_collection_id:int}",
    tags=["Sub-Collection-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def edit_sub_collection(
    bg: BackgroundTasks,
    sub_collection_id: int = Depends(check_sub_collection_existence_by_id_dp),
    title: str | None = Form(None),
    image: UploadFile | None = File(None),
    slug_tag: str | None = Form(None),
    title_tag: str | None = Form(None),
    description_tag: str | None = Form(None),
    services: SubCollectionServices = Depends(
        sub_collection_services_dp,
    ),
):
    return await services.edit_sub_collection_service(
        title,
        image,
        slug_tag,
        title_tag,
        description_tag,
        sub_collection_id,
        bg,
    )


@sub_collection_router.delete(
    path="/delete-sub-collection/{sub_collection_id:int}",
    tags=["Sub-Collection-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def delete_sub_collection(
    sub_collection_id: int = Depends(check_sub_collection_existence_by_id_dp),
    services: SubCollectionServices = Depends(
        sub_collection_services_dp,
    ),
):
    return await services.delete_sub_collection_service(sub_collection_id)
