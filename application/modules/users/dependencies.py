from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from application.core.database import get_db
from application.modules.users.repository import UserRepository
from application.modules.users.services import UserServices


async def user_services_dp(session: AsyncSession = Depends(get_db)) -> UserServices:
    repo = UserRepository(session)
    return UserServices(repo)
