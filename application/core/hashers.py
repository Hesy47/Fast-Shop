from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError, HashingError
from argon2.low_level import Type
from fastapi import HTTPException, status


class CustomArgon2Hasher:
    ARGON2_HASHER = PasswordHasher(
        time_cost=3,
        memory_cost=72 * 1024,
        parallelism=2,
        hash_len=36,
        salt_len=18,
        type=Type.ID,
    )

    @staticmethod
    def create_hashed_password_for_route(password: str):
        try:
            return CustomArgon2Hasher.ARGON2_HASHER.hash(password)
        except HashingError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Something went wrong on hashing",
            )

    @staticmethod
    def verify_hashed_password_for_route(password: str, hashed_password: str):
        try:
            return CustomArgon2Hasher.ARGON2_HASHER.verify(
                password=password,
                hash=hashed_password,
            )
        except (InvalidHashError, VerifyMismatchError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid credentials",
            )

    @staticmethod
    def create_hashed_password_raw(password: str):
        try:
            return CustomArgon2Hasher.ARGON2_HASHER.hash(password)
        except HashingError:
            raise ValueError("Something went wrong on hashing")

    @staticmethod
    def verify_hashed_password_raw(password: str, hashed_password: str):
        try:
            return CustomArgon2Hasher.ARGON2_HASHER.verify(
                password=password,
                hash=hashed_password,
            )
        except (InvalidHashError, VerifyMismatchError):
            raise ValueError("Invalid credentials")
