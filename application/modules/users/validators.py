from re import match

from application.modules.users.models import UserType


class CustomUserValidator:

    @staticmethod
    def username_validator(value: str) -> None:
        if not 4 <= len(value) <= 25:
            raise ValueError("The username can be between 4 to 25 characters long")

        if not bool(match(pattern=r"^(?=.*[A-Za-z])[A-Za-z0-9_]+$", string=value)):
            raise ValueError(
                "Username can only contains letters, numbers and _ and it must have at least one letter"
            )

        return None

    @staticmethod
    def phone_number_validator(value: str) -> None:
        if not value.isnumeric():
            raise ValueError("Phone number must be numerical")

        if not len(value) == 11:
            raise ValueError("Phone number must be exact 11 numbers long")

        return None

    @staticmethod
    def password_validator(value: str) -> None:
        if not 8 <= len(value):
            raise ValueError("The password must be at least 8 character long")

        if not bool(
            match(
                pattern=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$", string=value
            )
        ):
            raise ValueError(
                "The password must contain at least one uppercase letter, one lowercased letter and a number in it"
            )

        return None

    @staticmethod
    def user_type_validator(value: str) -> None:
        valid_user_types = (UserType.admin.value, UserType.customer.value)

        if not value in valid_user_types:
            raise ValueError(f"The valid user types are: {valid_user_types}")

        return None
