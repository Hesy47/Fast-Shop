from fastapi import BackgroundTasks, File, HTTPException, Request, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from application.modules.sub_collections.pagination import (
    CustomSubCollectionPaginationResponse,
)
from application.modules.sub_collections.repository import SubCollectionRepository
from application.modules.sub_collections.schemas import (
    CreateSubCollectionRequest,
    EditSubCollectionRequest,
    GetAllSubCollectionsResponse,
    GetSubCollectionResponse,
    PublicGetAllSubCollectionsResponse,
    PublicGetSubCollectionResponse,
)
from application.shared.exceptions import CustomExceptionsHandlers
from application.shared.storage import DiskManager


class SubCollectionServices:
    def __init__(self, repo: SubCollectionRepository):
        self.repo = repo

    async def public_get_sub_collection_service(
        self, sub_collection_id: int, request: Request
    ):
        sub_collection_repository = (
            await self.repo.public_get_sub_collection_repository(sub_collection_id)
        )

        if not sub_collection_repository:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="We do not have such this sub collection",
            )

        return PublicGetSubCollectionResponse(
            id=sub_collection_repository.id,
            title=sub_collection_repository.title,
            image=f"{request.base_url}{DiskManager.COLLECTIONS_SAVE_PATH}{sub_collection_repository.image}",
        )

    async def public_get_all_sub_collections_service(
        self,
        page,
        per_page,
        order_by,
        search,
        limit,
        offset,
        request: Request,
        route_path,
    ):
        if per_page > 20:
            raise HTTPException(
                detail="maximum item per page is 20",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if not await self.repo.valid_order_by(order_by):
            raise HTTPException(
                detail=f"valid order_by choices are: {list(self.repo.VALID_ORDERING_CHOICES.keys())}",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        total_sub_collection_repository = await self.repo.count_all_sub_collections(
            search
        )
        sub_collection_repository = (
            await self.repo.public_get_all_sub_collections_repository(
                limit, offset, order_by, search
            )
        )
        paginated_responses = CustomSubCollectionPaginationResponse(
            page,
            per_page,
            limit,
            offset,
            request.base_url,
            route_path,
            total_sub_collection_repository,
        )

        return PublicGetAllSubCollectionsResponse(
            count=total_sub_collection_repository,
            next=paginated_responses.the_next(),
            previous=paginated_responses.the_previous(),
            total_pages=paginated_responses.total_pages(),
            current_page=page,
            results=[
                {
                    "id": sub_collection.id,
                    "title": sub_collection.title,
                    "image": f"{request.base_url}{DiskManager.SUB_COLLECTIONS_SAVE_PATH}{sub_collection.image}",
                }
                for sub_collection in sub_collection_repository
            ],
        )

    async def get_sub_collection_service(
        self, sub_collection_id: int, request: Request
    ):
        sub_collection_repository = await self.repo.get_sub_collection_repository(
            sub_collection_id
        )

        if not sub_collection_repository:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="We do not have such this sub collection",
            )

        return GetSubCollectionResponse(
            id=sub_collection_repository.id,
            title=sub_collection_repository.title,
            image=f"{request.base_url}{DiskManager.SUB_COLLECTIONS_SAVE_PATH}{sub_collection_repository.image}",
            created_at=sub_collection_repository.created_at,
            updated_at=sub_collection_repository.updated_at,
        )

    async def get_all_sub_collections_service(
        self,
        page,
        per_page,
        order_by,
        search,
        limit,
        offset,
        request: Request,
        route_path,
    ):
        if not await self.repo.valid_order_by(order_by):
            raise HTTPException(
                detail=f"valid order_by choices are: {list(self.repo.VALID_ORDERING_CHOICES.keys())}",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        total_sub_collection_repository = await self.repo.count_all_sub_collections(
            search
        )
        sub_collection_repository = await self.repo.get_all_collections_repository(
            limit, offset, order_by, search
        )
        paginated_responses = CustomSubCollectionPaginationResponse(
            page,
            per_page,
            limit,
            offset,
            request.base_url,
            route_path,
            total_sub_collection_repository,
        )

        return GetAllSubCollectionsResponse(
            count=total_sub_collection_repository,
            next=paginated_responses.the_next(),
            previous=paginated_responses.the_previous(),
            total_pages=paginated_responses.total_pages(),
            current_page=page,
            results=[
                {
                    "id": sub_collection.id,
                    "title": sub_collection.title,
                    "image": f"{request.base_url}{DiskManager.SUB_COLLECTIONS_SAVE_PATH}{sub_collection.image}",
                    "created_at": sub_collection.created_at,
                    "updated_at": sub_collection.updated_at,
                }
                for sub_collection in sub_collection_repository
            ],
        )

    async def create_sub_collection_service(
        self,
        title: str,
        image: UploadFile,
        bg: BackgroundTasks,
    ):
        if not int(image.size) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "field": "image",
                    "status": status.HTTP_400_BAD_REQUEST,
                    "type": "missing",
                    "error": "Field is required",
                },
            )

        if await self.repo.check_is_unique_title_repository_for_create(title):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "field": "title",
                    "status": status.HTTP_400_BAD_REQUEST,
                    "type": "value_error",
                    "error": "This title is already taken",
                },
            )

        image_filename = DiskManager.image_title_webp_convertor_for_route(
            image.filename
        )

        if await self.repo.check_is_unique_image_repository_for_create(image_filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "field": "image",
                    "status": status.HTTP_400_BAD_REQUEST,
                    "type": "value_error",
                    "error": "This image is already taken",
                },
            )

        try:
            payload = CreateSubCollectionRequest(title=title, image=image_filename)
        except ValidationError as error:
            await CustomExceptionsHandlers.pydantic_validation_handler_for_route(error)

        await self.repo.create_sub_collection_repository(payload)

        image_file = await image.read()

        bg.add_task(
            DiskManager.upload_image_for_route,
            DiskManager.image_processor_for_route(image_file, quality=85),
            f"{DiskManager.SUB_COLLECTIONS_SAVE_PATH}{image_filename}",
        )

        return JSONResponse(
            content={"message": "New sub collection created successfully"},
            status_code=status.HTTP_201_CREATED,
        )

    async def edit_sub_collection_service(
        self,
        title: str,
        image: UploadFile,
        sub_collection_id: int,
        bg: BackgroundTasks,
    ):

        if title:
            if await self.repo.check_is_unique_title_repository_for_edit(
                title,
                sub_collection_id,
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "field": "title",
                        "status": status.HTTP_400_BAD_REQUEST,
                        "type": "value_error",
                        "error": "This title is already taken",
                    },
                )

        if int(image.size) > 0:
            image_filename = DiskManager.image_title_webp_convertor_for_route(
                image.filename
            )

            if await self.repo.check_is_unique_image_repository_for_edit(
                image_filename,
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "field": "image",
                        "status": status.HTTP_400_BAD_REQUEST,
                        "type": "value_error",
                        "error": "This image is already taken",
                    },
                )
        else:
            image_filename = None

        try:
            payload = EditSubCollectionRequest(title=title, image=image_filename)
        except ValidationError as error:
            await CustomExceptionsHandlers.pydantic_validation_handler_for_route(error)

        await self.repo.edit_sub_collection_repository(payload, sub_collection_id)

        if int(image.size) > 0:
            image_file = await image.read()

            bg.add_task(
                DiskManager.upload_image_for_route,
                DiskManager.image_processor_for_route(image_file, quality=85),
                f"{DiskManager.SUB_COLLECTIONS_SAVE_PATH}{image_filename}",
            )

        return JSONResponse(
            content={"message": "sub collection updated successfully"},
            status_code=status.HTTP_200_OK,
        )

    async def delete_sub_collection_service(self, sub_collection_id: int):
        await self.repo.delete_sub_collection_repository(sub_collection_id)
        return JSONResponse(
            content={"message": "Sub Collection has been deleted successfully"},
            status_code=status.HTTP_200_OK,
        )
