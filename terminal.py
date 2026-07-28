import asyncio
from getpass import getpass
from secrets import token_urlsafe

from sqlalchemy import or_, select

from application.core.database import AsyncSessionLocal
from application.core.hashers import CustomArgon2Hasher
from application.modules.users.models import User, UserType


def create_tokens_secret():
    print(token_urlsafe(85), "\n")


async def create_admin_user():
    while True:
        username = input("username: ").strip()
        if not 4 <= len(username) <= 30:
            print("username must be between 4 to 30 characters long\n")
            continue

        phone_number = input("phone number: ").strip()
        if not phone_number.isnumeric() or len(phone_number) != 11:
            print("please inter a valid phone number\n")
            continue

        password = getpass("password: ")
        if not 8 <= len(password):
            print("password must be at least 8 characters long\n")
            continue

        password_confirm = getpass("password confirm: ")
        if password != password_confirm:
            print("password and password confirm must be similar\n")
            continue

        async with AsyncSessionLocal() as session:
            try:
                admin_user_exist_query = select(User.id).where(
                    or_(
                        User.username == username,
                        User.phone_number == phone_number,
                    )
                )

                admin_user_exist_operation = await session.execute(
                    admin_user_exist_query
                )

                admin_user_exist_result = admin_user_exist_operation.first()
                if admin_user_exist_result:
                    print(
                        "We already have a admin with this username or phone number\n"
                    )
                    continue

                new_admin_user = User(
                    username=username,
                    phone_number=phone_number,
                    password=CustomArgon2Hasher.create_hashed_password_raw(password),
                    user_type=UserType.admin.value,
                    is_active=True,
                )

                session.add(new_admin_user)
                await session.commit()

                print("New admin user created successfully\n")
                break

            except Exception as database_error:
                await session.rollback()
                raise database_error

            finally:
                await session.close()


if __name__ == "__main__":
    while True:
        VALID_COMMANDS = {
            "1": "Create admin user",
            "2": "The name of creator",
            "3": "Generate JWT secret",
            "0": "Exit from command line",
        }
        print("Welcome to command line interface, you can choice from commands bellow:")

        for key, value in VALID_COMMANDS.items():
            print(f"{key}.{value}")

        user_choice = input("\nCommand code: ")
        if not user_choice in VALID_COMMANDS:
            print("Invalid command code\n")
            continue

        if user_choice == "1":
            asyncio.run(create_admin_user())
            continue

        if user_choice == "2":
            print("Amir Hesam Karim zadeh\n")
            continue

        if user_choice == "3":
            create_tokens_secret()
            continue

        if user_choice == "0":
            print("Good Luck...")
            break
