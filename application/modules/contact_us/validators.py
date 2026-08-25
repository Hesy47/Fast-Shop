import re


class CustomContactUsValidator:
    @staticmethod
    def subject_validator(value: str) -> None:
        if len(value) > 100:
            raise ValueError("موضوع تیکت نباید بیشتر از 100 کاراکتر باشد")

        if len(value) < 3:
            raise ValueError("موضوع تیکت نباید کمتر از 3 کاراکتر باشد")

    @staticmethod
    def message_validator(value: str) -> None:
        if len(value) > 500:
            raise ValueError("متن تیکت نباید بیشتر از 500 کاراکتر باشد")

        if len(value) < 7:
            raise ValueError("متن تیکت نباید کمتر از 7 کاراکتر باشد")

    @staticmethod
    def phone_number_validator(value: str) -> None:
        if re.fullmatch(r"09[0-9]{9}", value) is None:
            raise ValueError("لطفا یک شماره همراه معتبر وارد کنید")
