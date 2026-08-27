from typing import Type

from fastapi import BackgroundTasks, HTTPException, Request, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError

from application.modules.banners.pagination import CustomBannerPaginationResponse
from application.modules.banners.repository import (
    BannerRepository,
    DesktopBannerRepository,
    PhoneBannerRepository,
)
from application.modules.banners.schemas import (
    CreateDesktopBannerRequest,
    CreatePhoneBannerRequest,
    EditDesktopBannerRequest,
    EditPhoneBannerRequest,
    GetAllDesktopBannersResponse,
    GetAllPhoneBannersResponse,
    GetDesktopBannerResponse,
    GetPhoneBannerResponse,
    PublicDesktopBannerResponse,
    PublicGetAllDesktopBannersResponse,
    PublicGetAllPhoneBannersResponse,
    PublicPhoneBannerResponse,
)
from application.shared.exceptions import CustomExceptionsHandlers
from application.shared.storage import DiskManager


class BannerServices:
    banner_name: str
    save_path: str
    create_schema: Type[BaseModel]
    edit_schema: Type[BaseModel]
    public_response_schema: Type[BaseModel]
    public_list_response_schema: Type[BaseModel]
    admin_response_schema: Type[BaseModel]
    admin_list_response_schema: Type[BaseModel]

    def __init__(self, repo: BannerRepository):
        self.repo = repo

    def serialize_public_banner(self, banner, request: Request):
        return self.public_response_schema(
            id=banner.id,
            title=banner.title,
            image=f"{request.base_url}{self.save_path}{banner.image}",
        )

    def serialize_admin_banner(self, banner, request: Request):
        return self.admin_response_schema(
            id=banner.id,
            title=banner.title,
            image=f"{request.base_url}{self.save_path}{banner.image}",
            created_at=banner.created_at,
            updated_at=banner.updated_at,
        )

    async def public_get_banner_service(self, banner_id: int, request: Request):
        banner = await self.repo.get_public_banner_repository(banner_id)
        if not banner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"We do not have such this {self.banner_name} banner",
            )
        return self.serialize_public_banner(banner, request)

    async def public_get_all_banners_service(
        self,
        page: int,
        per_page: int,
        order_by: str,
        search: str,
        limit: int,
        offset: int,
        request: Request,
        route_path: str,
    ):
        if per_page > 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="maximum item per page is 20",
            )
        return await self._get_all_banners_response(
            page,
            per_page,
            order_by,
            search,
            limit,
            offset,
            request,
            route_path,
            is_public=True,
        )

    async def get_banner_service(self, banner_id: int, request: Request):
        banner = await self.repo.get_banner_repository(banner_id)
        if not banner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"We do not have such this {self.banner_name} banner",
            )
        return self.serialize_admin_banner(banner, request)

    async def get_all_banners_service(
        self,
        page: int,
        per_page: int,
        order_by: str,
        search: str,
        limit: int,
        offset: int,
        request: Request,
        route_path: str,
    ):
        return await self._get_all_banners_response(
            page,
            per_page,
            order_by,
            search,
            limit,
            offset,
            request,
            route_path,
            is_public=False,
        )

    async def _get_all_banners_response(
        self,
        page: int,
        per_page: int,
        order_by: str,
        search: str,
        limit: int,
        offset: int,
        request: Request,
        route_path: str,
        is_public: bool,
    ):
        if not self.repo.valid_order_by(order_by):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "valid order_by choices are: "
                    f"{list(self.repo.valid_ordering_choices.keys())}"
                ),
            )

        total = await self.repo.count_all_banners(search)
        if is_public:
            banners = await self.repo.get_public_all_banners_repository(
                limit, offset, order_by, search
            )
            results = [self.serialize_public_banner(item, request) for item in banners]
            response_schema = self.public_list_response_schema
        else:
            banners = await self.repo.get_all_banners_repository(
                limit, offset, order_by, search
            )
            results = [self.serialize_admin_banner(item, request) for item in banners]
            response_schema = self.admin_list_response_schema

        pagination = CustomBannerPaginationResponse(
            page,
            per_page,
            limit,
            offset,
            request.base_url,
            route_path,
            total,
        )
        return response_schema(
            count=total,
            next=pagination.the_next(),
            previous=pagination.the_previous(),
            total_pages=pagination.total_pages(),
            current_page=page,
            results=results,
        )

    async def create_banner_service(
        self,
        title: str,
        image: UploadFile,
        bg: BackgroundTasks,
    ):
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

        if await self.repo.check_unique_title_for_create(title):
            self._raise_unique_error("title")

        image_filename = DiskManager.image_title_webp_convertor_for_route(
            image.filename
        )
        if await self.repo.check_unique_image_for_create(image_filename):
            self._raise_unique_error("image")

        try:
            payload = self.create_schema(title=title, image=image_filename)
        except ValidationError as error:
            await CustomExceptionsHandlers.pydantic_validation_handler_for_route(error)

        await self.repo.create_banner_repository(payload)
        image_file = await image.read()
        bg.add_task(
            DiskManager.upload_image_for_route,
            DiskManager.image_processor_for_route(
                image_file, quality=90, width=2000, height=2000
            ),
            f"{self.save_path}{image_filename}",
        )
        return JSONResponse(
            content={"message": f"New {self.banner_name} banner created successfully"},
            status_code=status.HTTP_201_CREATED,
        )

    async def edit_banner_service(
        self,
        title: str | None,
        image: UploadFile | None,
        banner_id: int,
        bg: BackgroundTasks,
    ):
        if title and await self.repo.check_unique_title_for_edit(title, banner_id):
            self._raise_unique_error("title")

        has_image = image is not None and bool(image.size)
        image_filename = None
        if has_image:
            image_filename = DiskManager.image_title_webp_convertor_for_route(
                image.filename
            )
            if await self.repo.check_unique_image_for_edit(image_filename, banner_id):
                self._raise_unique_error("image")

        try:
            payload = self.edit_schema(title=title, image=image_filename)
        except ValidationError as error:
            await CustomExceptionsHandlers.pydantic_validation_handler_for_route(error)

        await self.repo.edit_banner_repository(payload, banner_id)
        if has_image:
            image_file = await image.read()
            bg.add_task(
                DiskManager.upload_image_for_route,
                DiskManager.image_processor_for_route(
                    image_file, quality=90, width=2000, height=2000
                ),
                f"{self.save_path}{image_filename}",
            )
        return JSONResponse(
            content={
                "message": f"{self.banner_name.title()} banner updated successfully"
            },
            status_code=status.HTTP_200_OK,
        )

    async def delete_banner_service(self, banner_id: int):
        await self.repo.delete_banner_repository(banner_id)
        return JSONResponse(
            content={
                "message": f"{self.banner_name.title()} banner has been deleted successfully"
            },
            status_code=status.HTTP_200_OK,
        )

    @staticmethod
    def _raise_unique_error(field: str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "field": field,
                "status": status.HTTP_400_BAD_REQUEST,
                "type": "value_error",
                "error": f"This {field} is already taken",
            },
        )


class DesktopBannerServices(BannerServices):
    banner_name = "desktop"
    save_path = DiskManager.DESKTOP_BANNERS_SAVE_PATH
    create_schema = CreateDesktopBannerRequest
    edit_schema = EditDesktopBannerRequest
    public_response_schema = PublicDesktopBannerResponse
    public_list_response_schema = PublicGetAllDesktopBannersResponse
    admin_response_schema = GetDesktopBannerResponse
    admin_list_response_schema = GetAllDesktopBannersResponse

    def __init__(self, repo: DesktopBannerRepository):
        super().__init__(repo)


class PhoneBannerServices(BannerServices):
    banner_name = "phone"
    save_path = DiskManager.PHONE_BANNERS_SAVE_PATH
    create_schema = CreatePhoneBannerRequest
    edit_schema = EditPhoneBannerRequest
    public_response_schema = PublicPhoneBannerResponse
    public_list_response_schema = PublicGetAllPhoneBannersResponse
    admin_response_schema = GetPhoneBannerResponse
    admin_list_response_schema = GetAllPhoneBannersResponse

    def __init__(self, repo: PhoneBannerRepository):
        super().__init__(repo)
