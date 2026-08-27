from datetime import datetime, timedelta
from uuid import uuid4
from zoneinfo import ZoneInfo

import jwt
from fastapi import HTTPException, status
from jwt.exceptions import ExpiredSignatureError

from application.shared import env_variables


class CustomJWTAuthentication:
    JWT_ACCESS_TOKEN_SECRET = env_variables.JWT_ACCESS_TOKEN_SECRET
    JWT_REFRESH_TOKEN_SECRET = env_variables.JWT_REFRESH_TOKEN_SECRET
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_TIME_IN_HOUR = 1
    REFRESH_TOKEN_EXPIRE_TIME_IN_DAY = 7

    @staticmethod
    def create_access_token_for_route(data: dict):
        to_encode = data.copy()
        expire = datetime.now(ZoneInfo("Asia/Tehran")) + timedelta(
            hours=CustomJWTAuthentication.ACCESS_TOKEN_EXPIRE_TIME_IN_HOUR
        )

        to_encode.update(
            {
                "exp": expire,
                "type": "AccessToken",
                "iat": datetime.now(ZoneInfo("Asia/Tehran")),
                "nbf": datetime.now(ZoneInfo("Asia/Tehran")),
                "jti": str(uuid4()),
            }
        )

        encoded_access_token = jwt.encode(
            payload=to_encode,
            key=CustomJWTAuthentication.JWT_ACCESS_TOKEN_SECRET,
            algorithm=CustomJWTAuthentication.ALGORITHM,
        )

        return encoded_access_token

    @staticmethod
    def create_refresh_token_for_route(data: dict):
        to_encode = data.copy()
        expire = datetime.now(ZoneInfo("Asia/Tehran")) + timedelta(
            days=CustomJWTAuthentication.REFRESH_TOKEN_EXPIRE_TIME_IN_DAY
        )

        to_encode.update(
            {
                "exp": expire,
                "type": "RefreshToken",
                "iat": datetime.now(ZoneInfo("Asia/Tehran")),
                "nbf": datetime.now(ZoneInfo("Asia/Tehran")),
                "jti": str(uuid4()),
            }
        )

        encoded_refresh_token = jwt.encode(
            payload=to_encode,
            key=CustomJWTAuthentication.JWT_REFRESH_TOKEN_SECRET,
            algorithm=CustomJWTAuthentication.ALGORITHM,
        )

        return encoded_refresh_token

    @staticmethod
    def verify_access_token_for_route(token: str):
        try:
            decoded_access_token = jwt.decode(
                jwt=token,
                key=CustomJWTAuthentication.JWT_ACCESS_TOKEN_SECRET,
                algorithms=[CustomJWTAuthentication.ALGORITHM],
            )

            return decoded_access_token

        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="your access token is expired",
            )

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="invalid access token",
            )

    @staticmethod
    def verify_refresh_token_for_route(token: str):
        try:
            decoded_refresh_token = jwt.decode(
                jwt=token,
                key=CustomJWTAuthentication.JWT_REFRESH_TOKEN_SECRET,
                algorithms=[CustomJWTAuthentication.ALGORITHM],
            )

            return decoded_refresh_token

        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="your refresh token is expired",
            )

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="invalid refresh token",
            )
