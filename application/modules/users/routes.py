from fastapi import APIRouter, Depends, Request

from application.core.permissions import CustomPermissions
from application.modules.users.dependencies import (
    check_user_existence_by_id_dp,
    user_services_dp,
    user_without_authorization_dp,
)
from application.modules.users.pagination import CustomUserPaginationParams
from application.modules.users.schemas import (
    BasicLoginRequest,
    CreateUserRequest,
    EditUserRequest,
    GetAllUsersResponse,
    GetUserResponse,
)
from application.modules.users.services import UserServices

user_router = APIRouter(prefix="/api")


@user_router.post(
    path="/basic-login",
    tags=["User-Public"],
    dependencies=[Depends(user_without_authorization_dp)],
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
    dependencies=[Depends(CustomPermissions.is_admin)],
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
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def get_all_users(
    request: Request,
    params: CustomUserPaginationParams = Depends(),
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


@user_router.post(
    path="/create_user",
    tags=["User-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def create_user(
    payload: CreateUserRequest,
    services: UserServices = Depends(
        user_services_dp,
    ),
):
    return await services.create_user_service(payload)


@user_router.patch(
    path="/edit_user/{user_id:int}",
    tags=["User-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def edit_user(
    user_id: int = Depends(check_user_existence_by_id_dp),
    payload: EditUserRequest = ...,
    services: UserServices = Depends(
        user_services_dp,
    ),
):
    return await services.edit_user_service(payload, user_id)


@user_router.delete(
    path="/delete_user/{user_id:int}",
    tags=["User-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def delete_user(
    user_id: int = Depends(check_user_existence_by_id_dp),
    services: UserServices = Depends(
        user_services_dp,
    ),
):
    return await services.delete_user_service(user_id)
