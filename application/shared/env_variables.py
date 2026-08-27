import os

from dotenv import load_dotenv

load_dotenv()

DEBUG = str(os.environ.get("DEBUG", ""))
DATABASE_URL = str(os.environ.get("DATABASE_URL", ""))
JWT_ACCESS_TOKEN_SECRET = str(os.environ.get("JWT_ACCESS_TOKEN_SECRET", ""))
JWT_REFRESH_TOKEN_SECRET = str(os.environ.get("JWT_REFRESH_TOKEN_SECRET", ""))
FRONTEND_URL = str(os.environ.get("FRONTEND_URL", ""))

if DEBUG.lower() == "true":
    DEBUG = True
else:
    DEBUG = False
