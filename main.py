from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles

from application.modules.users.routes import user_router
from application.modules.collections.routes import collection_router
from application.modules.sub_collections.routes import sub_collection_router
from application.shared.exceptions import CustomExceptionsHandlers
from application.shared.storage import DiskManager


@asynccontextmanager
async def startup_events(app: FastAPI):
    print("Application events starting...")

    await DiskManager.create_application_folders()
    app.mount("/media", StaticFiles(directory="media"), name="media")

    yield
    print("Application events ended...")


app = FastAPI(lifespan=startup_events)

app.include_router(user_router)
app.include_router(collection_router)
app.include_router(sub_collection_router)

app.add_exception_handler(
    RequestValidationError, CustomExceptionsHandlers.pydantic_validation_handler
)

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000)
0
