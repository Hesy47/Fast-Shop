from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import and_, or_, select

from application.modules.users.models import User, UserType
from application.core.database import AsyncSession, get_db
from application.core.tokens import CustomJWTAuthentication

auth_schema = HTTPBearer()


class CustomPermissions:
    async def is_admin(
        user_credentials: HTTPAuthorizationCredentials = Depends(auth_schema),
        db: AsyncSession = Depends(get_db),
    ):

        user_token = user_credentials.credentials
        verify_user_token = CustomJWTAuthentication.verify_access_token_for_route(
            user_token
        )
        verified_user_id = verify_user_token.get("id")

        get_user_query = select(User.id).where(
            and_(
                User.id == verified_user_id,
                User.user_type == UserType.admin,
                User.is_active == True,
            )
        )

        get_user_operation = await db.execute(get_user_query)
        get_user_result = get_user_operation.first()

        if not get_user_result:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )

    async def is_authenticated(
        user_credentials: HTTPAuthorizationCredentials = Depends(auth_schema),
        db: AsyncSession = Depends(get_db),
    ):

        user_token = user_credentials.credentials
        verify_user_token = CustomJWTAuthentication.verify_access_token_for_route(
            user_token
        )
        verified_user_id = verify_user_token.get("id")

        get_user_query = select(User.id).where(
            or_(
                and_(
                    User.id == verified_user_id,
                    User.user_type == UserType.admin,
                    User.is_active == True,
                ),
                and_(
                    User.id == verified_user_id,
                    User.user_type == UserType.customer,
                    User.is_active == True,
                ),
            )
        )

        get_user_operation = await db.execute(get_user_query)
        get_user_result = get_user_operation.first()

        if not get_user_result:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )

        return verify_user_token
