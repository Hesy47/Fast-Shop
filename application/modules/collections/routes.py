from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, UploadFile
from pydantic import ValidationError

from application.core.permissions import CustomPermissions
from application.modules.collections.dependencies import collection_services_dp
from application.modules.collections.schemas import CreateCollectionRequest
from application.modules.collections.services import CollectionServices
from application.shared.exceptions import CustomExceptionsHandlers

collection_router = APIRouter(prefix="/api")


@collection_router.post(
    path="/create-collection",
    tags=["Collection-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def create_collection(
    bg: BackgroundTasks,
    title: str = Form(),
    image: UploadFile = File(),
    service: CollectionServices = Depends(collection_services_dp),
):
    try:
        payload = CreateCollectionRequest(title=title, image=image.filename)
    except ValidationError as error:
        await CustomExceptionsHandlers.pydantic_validation_handler_for_route(error)

    return await service.create_collection_service(payload, bg, image)
