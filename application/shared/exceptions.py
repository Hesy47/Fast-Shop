from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class CustomExceptionsHandlers:

    @staticmethod
    async def pydantic_validation_handler(
        request: Request, exc: RequestValidationError
    ):
        reformatted_errors = []

        for error in exc.errors():
            field_name = error["loc"][-1] if error["loc"] else "unknown"
            error_status = status.HTTP_400_BAD_REQUEST
            error_type = error["type"]
            error_detail = (
                error["msg"][13:] if error_type == "value_error" else error["msg"]
            )

            reformatted_errors.append(
                {
                    "field": field_name,
                    "status": error_status,
                    "type": error_type,
                    "error": error_detail,
                }
            )

        return JSONResponse(
            status_code=error_status,
            content={"detail": reformatted_errors},
        )

    @staticmethod
    async def pydantic_validation_handler_for_route(error: RequestValidationError):
        reformatted_errors = []
        for error in error.errors():
            field_name = error["loc"][-1] if error["loc"] else "unknown"
            error_status = status.HTTP_400_BAD_REQUEST
            error_type = error["type"]
            error_detail = (
                error["msg"][13:] if error_type == "value_error" else error["msg"]
            )

            reformatted_errors.append(
                {
                    "field": field_name,
                    "status": error_status,
                    "type": error_type,
                    "error": error_detail,
                }
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=reformatted_errors,
        )
