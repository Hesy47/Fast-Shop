from sqlalchemy import and_, asc, desc, func, or_, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from application.modules.users.models import User
from application.modules.users.schemas import (
    BasicLoginRequest,
    CreateUserRequest,
    EditUserRequest,
)


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def basic_login_repository(self, payload: BasicLoginRequest):
        user_credentials_query = select(User.id, User.password).where(
            or_(
                and_(User.username == payload.identifier, User.is_active == True),
                and_(User.phone_number == payload.identifier, User.is_active == True),
            )
        )

        user_credentials_operation = await self.session.execute(user_credentials_query)
        user_credentials_result = user_credentials_operation.first()

        return user_credentials_result

    VALID_ORDERING_CHOICES = {"id": asc(User.id), "-id": desc(User.id)}

    async def get_user_repository(self, user_id: int) -> None | User:
        get_user_query = select(
            User.id,
            User.username,
            User.phone_number,
            User.password,
            User.user_type,
            User.is_active,
            User.created_at,
            User.updated_at,
        ).where(User.id == user_id)

        get_user_operation = await self.session.execute(get_user_query)
        get_user_result = get_user_operation.first()

        return get_user_result

    async def get_all_users_repository(self, limit, offset, order_by, search):
        get_all_users_query = (
            select(
                User.id,
                User.username,
                User.phone_number,
                User.password,
                User.user_type,
                User.is_active,
                User.created_at,
                User.updated_at,
            )
            .limit(limit)
            .offset(offset)
            .order_by(self.VALID_ORDERING_CHOICES.get(order_by))
        )

        if search:
            get_all_users_query = get_all_users_query.where(
                or_(
                    User.username.ilike(f"%{search}%"),
                    User.phone_number.icontains(search),
                )
            )

        get_all_users_operation = await self.session.execute(get_all_users_query)
        get_all_users_results = get_all_users_operation.all()

        return get_all_users_results

    async def count_all_users(self, search):
        total_users_query = select(func.count(User.id))

        if search:
            total_users_query = total_users_query.where(
                or_(
                    User.username.ilike(f"%{search}%"),
                    User.phone_number.icontains(search),
                )
            )

        total_users_operation = await self.session.execute(total_users_query)
        total_users_result = total_users_operation.first()

        return total_users_result[0]

    async def valid_order_by(self, order_by):
        return order_by in self.VALID_ORDERING_CHOICES

    async def check_unique_username_repository_for_create(self, username: str):
        unique_username_query = select(User.id).where(User.username == username)
        unique_username_operation = await self.session.execute(unique_username_query)
        unique_username_result = unique_username_operation.first()

        return unique_username_result

    async def check_unique_phone_number_repository_for_create(self, phone_number: str):
        unique_phone_number_query = select(User.id).where(
            User.phone_number == phone_number
        )
        unique_phone_number_operation = await self.session.execute(
            unique_phone_number_query
        )
        unique_phone_number_result = unique_phone_number_operation.first()

        return unique_phone_number_result

    async def create_user_repository(self, payload: CreateUserRequest):
        new_user = User(**payload.model_dump())

        self.session.add(new_user)
        await self.session.commit()

    async def check_unique_username_repository_for_edit(
        self, username: str, user_id: int
    ):
        unique_username_query = select(User.id).where(
            and_(User.username == username, User.id != user_id)
        )
        unique_username_operation = await self.session.execute(unique_username_query)
        unique_username_result = unique_username_operation.first()

        return unique_username_result

    async def check_unique_phone_number_repository_for_edit(
        self, phone_number: str, user_id: int
    ):
        unique_phone_number_query = select(User.id).where(
            and_(User.phone_number == phone_number, User.id != user_id)
        )
        unique_phone_number_operation = await self.session.execute(
            unique_phone_number_query
        )
        unique_phone_number_result = unique_phone_number_operation.first()

        return unique_phone_number_result

    async def edit_user_repository(self, payload: EditUserRequest, user_id: int):
        updated_user_data = payload.model_dump(exclude_none=True, exclude_unset=True)

        updated_user_query = (
            update(User).where(User.id == user_id).values(**updated_user_data)
        )

        await self.session.execute(updated_user_query)
        await self.session.commit()

    async def delete_user_repository(self, user_id: int):
        user_delete_query = delete(User).where(User.id == user_id)

        await self.session.execute(user_delete_query)
        await self.session.commit()
