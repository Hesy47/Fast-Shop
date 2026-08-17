from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

from application.modules.social_apps.pagination import (
    CustomSocialAppPaginationResponse,
)
from application.modules.social_apps.repository import SocialAppRepository
from application.modules.social_apps.schemas import (
    CreateSocialAppRequest,
    EditSocialAppRequest,
    GetAllSocialAppsResponse,
    GetSocialAppResponse,
    PublicGetAllSocialAppsResponse,
)


class SocialAppServices:
    def __init__(self, repo: SocialAppRepository):
        self.repo = repo

    async def public_get_all_social_apps_service(self):
        social_apps = await self.repo.public_get_all_social_apps_repository()
        return PublicGetAllSocialAppsResponse(
            root={item.title: item.link for item in social_apps}
        )

    async def get_social_app_service(self, social_app_id: int):
        social_app = await self.repo.get_social_app_repository(social_app_id)
        if not social_app:
            self._raise_not_found()
        return GetSocialAppResponse(**social_app._mapping)

    async def get_all_social_apps_service(
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
        if not self.repo.valid_order_by(order_by):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "valid order_by choices are: "
                    f"{list(self.repo.VALID_ORDERING_CHOICES.keys())}"
                ),
            )

        total = await self.repo.count_all_social_apps(search)
        social_apps = await self.repo.get_all_social_apps_repository(
            limit, offset, order_by, search
        )
        pagination = CustomSocialAppPaginationResponse(
            page,
            per_page,
            limit,
            offset,
            request.base_url,
            route_path,
            total,
        )
        return GetAllSocialAppsResponse(
            count=total,
            next=pagination.the_next(),
            previous=pagination.the_previous(),
            total_pages=pagination.total_pages(),
            current_page=page,
            results=[GetSocialAppResponse(**item._mapping) for item in social_apps],
        )

    async def create_social_app_service(self, payload: CreateSocialAppRequest):
        if await self.repo.check_unique_title_for_create(payload.title):
            self._raise_unique_title()
        await self.repo.create_social_app_repository(payload)
        return JSONResponse(
            content={"message": "New social app created successfully"},
            status_code=status.HTTP_201_CREATED,
        )

    async def edit_social_app_service(
        self,
        social_app_id: int,
        payload: EditSocialAppRequest,
    ):
        if payload.title and await self.repo.check_unique_title_for_edit(
            payload.title, social_app_id
        ):
            self._raise_unique_title()
        await self.repo.edit_social_app_repository(payload, social_app_id)
        return JSONResponse(
            content={"message": "Social app updated successfully"},
            status_code=status.HTTP_200_OK,
        )

    async def delete_social_app_service(self, social_app_id: int):
        await self.repo.delete_social_app_repository(social_app_id)
        return JSONResponse(
            content={"message": "Social app has been deleted successfully"},
            status_code=status.HTTP_200_OK,
        )

    @staticmethod
    def _raise_not_found():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="We do not have such this social app",
        )

    @staticmethod
    def _raise_unique_title():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "field": "title",
                "status": status.HTTP_400_BAD_REQUEST,
                "type": "value_error",
                "error": "This title is already taken",
            },
        )
