from fastapi import APIRouter, Depends, Request

from application.core.permissions import CustomPermissions
from application.modules.contact_us.dependencies import (
    check_contact_us_existence_by_id_dp,
    contact_us_services_dp,
)
from application.modules.contact_us.pagination import CustomContactUsPaginationParams
from application.modules.contact_us.schemas import (
    CreateContactUsRequest,
    EditContactUsRequest,
    PublicCreateContactUsRequest,
)
from application.modules.contact_us.services import ContactUsServices

contact_us_router = APIRouter(prefix="/api")


@contact_us_router.post(
    path="/contact-us",
    tags=["Contact-Us-Public"],
)
async def public_create_contact_us(
    payload: PublicCreateContactUsRequest,
    service: ContactUsServices = Depends(contact_us_services_dp),
):
    return await service.public_create_contact_us_service(payload)


@contact_us_router.get(
    path="/get-contact-us/{contact_us_id:int}",
    tags=["Contact-Us-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def get_contact_us(
    contact_us_id: int,
    service: ContactUsServices = Depends(contact_us_services_dp),
):
    return await service.get_contact_us_service(contact_us_id)


@contact_us_router.get(
    path="/get-all-contact-us",
    tags=["Contact-Us-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def get_all_contact_us(
    request: Request,
    params: CustomContactUsPaginationParams = Depends(),
    service: ContactUsServices = Depends(contact_us_services_dp),
):
    return await service.get_all_contact_us_service(
        params.page,
        params.per_page,
        params.ordering,
        params.search,
        params.limit,
        params.offset,
        request,
        "api/get-all-contact-us",
    )


@contact_us_router.post(
    path="/create-contact-us",
    tags=["Contact-Us-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def create_contact_us(
    payload: CreateContactUsRequest,
    service: ContactUsServices = Depends(contact_us_services_dp),
):
    return await service.create_contact_us_service(payload)


@contact_us_router.patch(
    path="/edit-contact-us/{contact_us_id:int}",
    tags=["Contact-Us-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def edit_contact_us(
    payload: EditContactUsRequest,
    contact_us_id: int = Depends(check_contact_us_existence_by_id_dp),
    service: ContactUsServices = Depends(contact_us_services_dp),
):
    return await service.edit_contact_us_service(contact_us_id, payload)


@contact_us_router.delete(
    path="/delete-contact-us/{contact_us_id:int}",
    tags=["Contact-Us-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def delete_contact_us(
    contact_us_id: int = Depends(check_contact_us_existence_by_id_dp),
    service: ContactUsServices = Depends(contact_us_services_dp),
):
    return await service.delete_contact_us_service(contact_us_id)
