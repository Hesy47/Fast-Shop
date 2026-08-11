from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Request, UploadFile

from application.core.permissions import CustomPermissions
from application.modules.banners.dependencies import (
    check_desktop_banner_existence_by_id_dp,
    check_phone_banner_existence_by_id_dp,
    desktop_banner_services_dp,
    phone_banner_services_dp,
)
from application.modules.banners.pagination import CustomBannerPaginationParams
from application.modules.banners.services import (
    DesktopBannerServices,
    PhoneBannerServices,
)

banner_router = APIRouter(prefix="/api")


@banner_router.get(
    path="/desktop-banners/{id:int}",
    tags=["Banner-Public"],
)
async def public_get_desktop_banner(
    request: Request,
    id: int,
    service: DesktopBannerServices = Depends(desktop_banner_services_dp),
):
    return await service.public_get_banner_service(id, request)


@banner_router.get(path="/desktop-banners", tags=["Banner-Public"])
async def public_get_all_desktop_banners(
    request: Request,
    params: CustomBannerPaginationParams = Depends(),
    service: DesktopBannerServices = Depends(desktop_banner_services_dp),
):
    return await service.public_get_all_banners_service(
        params.page,
        params.per_page,
        params.ordering,
        params.search,
        params.limit,
        params.offset,
        request,
        "api/desktop-banners",
    )


@banner_router.get(
    path="/phone-banners/{id:int}",
    tags=["Banner-Public"],
)
async def public_get_phone_banner(
    request: Request,
    id: int,
    service: PhoneBannerServices = Depends(phone_banner_services_dp),
):
    return await service.public_get_banner_service(id, request)


@banner_router.get(path="/phone-banners", tags=["Banner-Public"])
async def public_get_all_phone_banners(
    request: Request,
    params: CustomBannerPaginationParams = Depends(),
    service: PhoneBannerServices = Depends(phone_banner_services_dp),
):
    return await service.public_get_all_banners_service(
        params.page,
        params.per_page,
        params.ordering,
        params.search,
        params.limit,
        params.offset,
        request,
        "api/phone-banners",
    )


@banner_router.get(
    path="/get-desktop-banner/{desktop_banner_id:int}",
    tags=["Banner-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def get_desktop_banner(
    request: Request,
    desktop_banner_id: int,
    service: DesktopBannerServices = Depends(desktop_banner_services_dp),
):
    return await service.get_banner_service(desktop_banner_id, request)


@banner_router.get(
    path="/get-all-desktop-banners",
    tags=["Banner-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def get_all_desktop_banners(
    request: Request,
    params: CustomBannerPaginationParams = Depends(),
    service: DesktopBannerServices = Depends(desktop_banner_services_dp),
):
    return await service.get_all_banners_service(
        params.page,
        params.per_page,
        params.ordering,
        params.search,
        params.limit,
        params.offset,
        request,
        "api/get-all-desktop-banners",
    )


@banner_router.post(
    path="/create-desktop-banner",
    tags=["Banner-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def create_desktop_banner(
    bg: BackgroundTasks,
    title: str = Form(),
    image: UploadFile = File(),
    service: DesktopBannerServices = Depends(desktop_banner_services_dp),
):
    return await service.create_banner_service(title, image, bg)


@banner_router.patch(
    path="/edit-desktop-banner/{desktop_banner_id:int}",
    tags=["Banner-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def edit_desktop_banner(
    bg: BackgroundTasks,
    desktop_banner_id: int = Depends(check_desktop_banner_existence_by_id_dp),
    title: str | None = Form(None),
    image: UploadFile | None = File(None),
    service: DesktopBannerServices = Depends(desktop_banner_services_dp),
):
    return await service.edit_banner_service(title, image, desktop_banner_id, bg)


@banner_router.delete(
    path="/delete-desktop-banner/{desktop_banner_id:int}",
    tags=["Banner-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def delete_desktop_banner(
    desktop_banner_id: int = Depends(check_desktop_banner_existence_by_id_dp),
    service: DesktopBannerServices = Depends(desktop_banner_services_dp),
):
    return await service.delete_banner_service(desktop_banner_id)


@banner_router.get(
    path="/get-phone-banner/{phone_banner_id:int}",
    tags=["Banner-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def get_phone_banner(
    request: Request,
    phone_banner_id: int,
    service: PhoneBannerServices = Depends(phone_banner_services_dp),
):
    return await service.get_banner_service(phone_banner_id, request)


@banner_router.get(
    path="/get-all-phone-banners",
    tags=["Banner-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def get_all_phone_banners(
    request: Request,
    params: CustomBannerPaginationParams = Depends(),
    service: PhoneBannerServices = Depends(phone_banner_services_dp),
):
    return await service.get_all_banners_service(
        params.page,
        params.per_page,
        params.ordering,
        params.search,
        params.limit,
        params.offset,
        request,
        "api/get-all-phone-banners",
    )


@banner_router.post(
    path="/create-phone-banner",
    tags=["Banner-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def create_phone_banner(
    bg: BackgroundTasks,
    title: str = Form(),
    image: UploadFile = File(),
    service: PhoneBannerServices = Depends(phone_banner_services_dp),
):
    return await service.create_banner_service(title, image, bg)


@banner_router.patch(
    path="/edit-phone-banner/{phone_banner_id:int}",
    tags=["Banner-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def edit_phone_banner(
    bg: BackgroundTasks,
    phone_banner_id: int = Depends(check_phone_banner_existence_by_id_dp),
    title: str | None = Form(None),
    image: UploadFile | None = File(None),
    service: PhoneBannerServices = Depends(phone_banner_services_dp),
):
    return await service.edit_banner_service(title, image, phone_banner_id, bg)


@banner_router.delete(
    path="/delete-phone-banner/{phone_banner_id:int}",
    tags=["Banner-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def delete_phone_banner(
    phone_banner_id: int = Depends(check_phone_banner_existence_by_id_dp),
    service: PhoneBannerServices = Depends(phone_banner_services_dp),
):
    return await service.delete_banner_service(phone_banner_id)
