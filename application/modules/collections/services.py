from fastapi import BackgroundTasks, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from application.modules.collections.repository import CollectionRepository
from application.modules.collections.schemas import (
    CreateCollectionRequest,
    EditCollectionRequest,
)
from application.shared.storage import DiskManager


class CollectionServices:
    def __init__(self, repo: CollectionRepository):
        self.repo = repo

    async def create_collection_service(
        self, payload: CreateCollectionRequest, bg: BackgroundTasks, file: UploadFile
    ):
        if await self.repo.check_is_unique_title_repository_for_create(payload.title):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "field": "title",
                    "status": status.HTTP_400_BAD_REQUEST,
                    "type": "value_error",
                    "error": "This title is already taken",
                },
            )

        image_filename = DiskManager.image_title_webp_convertor_for_route(file.filename)

        if await self.repo.check_is_unique_image_repository_for_create(payload.image):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "field": "image",
                    "status": status.HTTP_400_BAD_REQUEST,
                    "type": "value_error",
                    "error": "This image is already taken",
                },
            )

        await self.repo.create_collection_repository(payload)

        image_file = await file.read()

        bg.add_task(
            DiskManager.upload_image_for_route,
            DiskManager.image_processor_for_route(image_file),
            f"{DiskManager.COLLECTIONS_SAVE_PATH}{image_filename}",
        )

        return JSONResponse(
            content={"message": "New user created successfully"},
            status_code=status.HTTP_201_CREATED,
        )
