from fastapi import Depends, HTTPException, status, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from application.core.database import get_db
from application.modules.users.repository import UserRepository
from application.modules.users.services import UserServices
from application.modules.users.models import User


async def user_services_dp(session: AsyncSession = Depends(get_db)) -> UserServices:
    repo = UserRepository(session)
    return UserServices(repo)


async def check_user_existence_by_id_dp(
    user_id: int, session: AsyncSession = Depends(get_db)
):
    user_exist_query = select(User.id).where(User.id == user_id)
    user_exist_operation = await session.execute(user_exist_query)
    user_exist_result = user_exist_operation.first()

    if not user_exist_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="we do not have such this user in our database",
        )

    return user_exist_result[0]


async def user_without_authorization_dp(request: Request):
    for header in request.headers.keys():
        if header.lower() == "authorization":
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Please logout first",
            )
