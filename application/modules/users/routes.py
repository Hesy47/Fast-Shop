from fastapi import APIRouter, Depends, Request

from application.modules.users.dependencies import user_services_dp
from application.modules.users.schemas import (
    BasicLoginRequest,
    GetAllUsersResponse,
    GetUserResponse,
)
from application.modules.users.services import UserServices
from application.shared.pagination import CustomPaginationParams

user_router = APIRouter(prefix="/api")


@user_router.post(
    path="/basic-login",
    tags=["User-Public"],
)
async def basic_login(
    payload: BasicLoginRequest,
    services: UserServices = Depends(
        user_services_dp,
    ),
):
    return await services.basic_login_service(payload)


@user_router.get(
    path="/get-user/{user_id:int}",
    tags=["User-Administration"],
    response_model=GetUserResponse,
)
async def get_user(
    user_id: int,
    services: UserServices = Depends(
        user_services_dp,
    ),
):
    return await services.get_user_service(user_id)


@user_router.get(
    path="/get-all-users",
    tags=["User-Administration"],
    response_model=GetAllUsersResponse,
)
async def get_all_users(
    request: Request,
    params: CustomPaginationParams = Depends(),
    services: UserServices = Depends(
        user_services_dp,
    ),
):

    return await services.get_all_users_service(
        params.page,
        params.per_page,
        params.ordering,
        params.search,
        params.limit,
        params.offset,
        request.base_url,
        "api/get-all-users",
    )
