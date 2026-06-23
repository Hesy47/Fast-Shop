from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from application.core.hashers import CustomArgon2Hasher
from application.core.tokens import CustomJWTAuthentication
from application.modules.users.repository import UserRepository
from application.modules.users.schemas import BasicLoginRequest, GetAllUsersResponse
from application.shared.pagination import CustomPaginationResponse


class UserServices:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def basic_login_service(self, payload: BasicLoginRequest):
        login_repository = await self.repo.basic_login_repository(payload)

        if not login_repository:
            raise HTTPException(
                detail="Invalid Credentials",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        CustomArgon2Hasher.verify_hashed_password_for_route(
            payload.password, login_repository.password
        )

        access_token, refresh_token = (
            CustomJWTAuthentication.create_access_token_for_route(
                {"id": login_repository.id}
            ),
            CustomJWTAuthentication.create_refresh_token_for_route(
                {"id": login_repository.id}
            ),
        )

        return JSONResponse(
            content={"access_token": access_token, "refresh_token": refresh_token},
            status_code=status.HTTP_202_ACCEPTED,
        )

    async def get_user_service(self, user_id: int):
        user_repository = await self.repo.get_user_repository(user_id)

        if not user_repository:
            raise HTTPException(
                detail="We do not have such this user in our database",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return user_repository

    async def get_all_users_service(
        self, page, per_page, order_by, search, limit, offset, base_url, route_path
    ):
        if not await self.repo.valid_order_by(order_by):
            raise HTTPException(
                detail=f"valid order_by choices are: {list(self.repo.VALID_ORDERING_CHOICES.keys())}",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        total_users_repository = await self.repo.count_all_users(search)
        users_repository = await self.repo.get_all_users_repository(
            limit, offset, order_by, search
        )
        paginated_responses = CustomPaginationResponse(
            page, per_page, limit, offset, base_url, route_path, total_users_repository
        )

        return GetAllUsersResponse(
            count=total_users_repository,
            next=paginated_responses.the_next(),
            previous=paginated_responses.the_previous(),
            total_pages=paginated_responses.total_pages(),
            current_page=page,
            results=[
                {
                    "id": user.id,
                    "username": user.username,
                    "phone_number": user.phone_number,
                    "password": user.password,
                    "user_type": user.user_type,
                    "is_active": user.is_active,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at,
                }
                for user in users_repository
            ],
        )
