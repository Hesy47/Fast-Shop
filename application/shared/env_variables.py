import os

from dotenv import load_dotenv

load_dotenv()

DEBUG = bool(os.environ.get("DEBUG", False))
DATABASE_URL = str(os.environ.get("DATABASE_URL", ""))
JWT_ACCESS_TOKEN_SECRET = str(os.environ.get("JWT_ACCESS_TOKEN_SECRET", ""))
JWT_REFRESH_TOKEN_SECRET = str(os.environ.get("JWT_REFRESH_TOKEN_SECRET", ""))
