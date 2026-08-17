from fastapi import APIRouter, Depends, Request

from application.core.permissions import CustomPermissions
from application.modules.social_apps.dependencies import (
    check_social_app_existence_by_id_dp,
    social_app_services_dp,
)
from application.modules.social_apps.pagination import (
    CustomSocialAppPaginationParams,
)
from application.modules.social_apps.schemas import (
    CreateSocialAppRequest,
    EditSocialAppRequest,
    PublicGetAllSocialAppsResponse,
)
from application.modules.social_apps.services import SocialAppServices

social_app_router = APIRouter(prefix="/api")


@social_app_router.get(
    path="/social-apps",
    tags=["Social-App-Public"],
    response_model=PublicGetAllSocialAppsResponse,
)
async def public_get_all_social_apps(
    service: SocialAppServices = Depends(social_app_services_dp),
):
    return await service.public_get_all_social_apps_service()


@social_app_router.get(
    path="/get-social-app/{social_app_id:int}",
    tags=["Social-App-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def get_social_app(
    social_app_id: int,
    service: SocialAppServices = Depends(social_app_services_dp),
):
    return await service.get_social_app_service(social_app_id)


@social_app_router.get(
    path="/get-all-social-apps",
    tags=["Social-App-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def get_all_social_apps(
    request: Request,
    params: CustomSocialAppPaginationParams = Depends(),
    service: SocialAppServices = Depends(social_app_services_dp),
):
    return await service.get_all_social_apps_service(
        params.page,
        params.per_page,
        params.ordering,
        params.search,
        params.limit,
        params.offset,
        request,
        "api/get-all-social-apps",
    )


@social_app_router.post(
    path="/create-social-app",
    tags=["Social-App-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def create_social_app(
    payload: CreateSocialAppRequest,
    service: SocialAppServices = Depends(social_app_services_dp),
):
    return await service.create_social_app_service(payload)


@social_app_router.patch(
    path="/edit-social-app/{social_app_id:int}",
    tags=["Social-App-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def edit_social_app(
    payload: EditSocialAppRequest,
    social_app_id: int = Depends(check_social_app_existence_by_id_dp),
    service: SocialAppServices = Depends(social_app_services_dp),
):
    return await service.edit_social_app_service(social_app_id, payload)


@social_app_router.delete(
    path="/delete-social-app/{social_app_id:int}",
    tags=["Social-App-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def delete_social_app(
    social_app_id: int = Depends(check_social_app_existence_by_id_dp),
    service: SocialAppServices = Depends(social_app_services_dp),
):
    return await service.delete_social_app_service(social_app_id)
