import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from application.modules.users.routes import user_router
from application.shared.exceptions import CustomExceptionsHandlers

app = FastAPI()

app.include_router(user_router)

app.add_exception_handler(
    RequestValidationError, CustomExceptionsHandlers.pydantic_validation_handler
)

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000)
