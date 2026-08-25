from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from application.modules.banners.routes import banner_router
from application.modules.collections.routes import collection_router
from application.modules.contact_us.routes import contact_us_router
from application.modules.products.routes import product_router
from application.modules.questions.routes import question_router
from application.modules.scrolls.routes import scroll_router
from application.modules.social_apps.routes import social_app_router
from application.modules.sub_collections.routes import sub_collection_router
from application.modules.users.routes import user_router
from application.shared.env_variables import DEBUG
from application.shared.exceptions import CustomExceptionsHandlers
from application.shared.storage import DiskManager


@asynccontextmanager
async def startup_events(app: FastAPI):
    print("Application events starting...")

    await DiskManager.create_application_folders()
    app.mount("/media", StaticFiles(directory="media"), name="media")

    yield
    print("Application events ended...")


app = FastAPI(
    lifespan=startup_events,
    title="Fast-Shop",
    description="The fully asynchronous FastAPI online shop application",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(collection_router)
app.include_router(sub_collection_router)
app.include_router(product_router)
app.include_router(banner_router)
app.include_router(scroll_router)
app.include_router(social_app_router)
app.include_router(question_router)
app.include_router(contact_us_router)

app.add_exception_handler(
    RequestValidationError, CustomExceptionsHandlers.pydantic_validation_handler
)

if __name__ == "__main__":
    if DEBUG:
        uvicorn.run(app="main:app", host="127.0.0.1", port=8000)

    if not DEBUG:
        uvicorn.run(app="main:app", host="0.0.0.0", port=8000)
