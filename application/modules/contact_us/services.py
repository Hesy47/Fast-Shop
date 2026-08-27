from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

from application.modules.contact_us.pagination import (
    CustomContactUsPaginationResponse,
)
from application.modules.contact_us.repository import ContactUsRepository
from application.modules.contact_us.schemas import (
    CreateContactUsRequest,
    EditContactUsRequest,
    GetAllContactUsResponse,
    GetContactUsResponse,
    PublicCreateContactUsRequest,
)


class ContactUsServices:
    def __init__(self, repo: ContactUsRepository):
        self.repo = repo

    async def public_create_contact_us_service(
        self,
        payload: PublicCreateContactUsRequest,
    ):
        await self.repo.create_contact_us_repository(payload)
        return JSONResponse(
            content={
                "message": "تیکت شما با موفقیت ثبت شد، بزودی کارشناسان ما با شما تماس خواهند گرفت"
            },
            status_code=status.HTTP_201_CREATED,
        )

    async def get_contact_us_service(self, contact_us_id: int):
        contact_us = await self.repo.get_contact_us_repository(contact_us_id)
        if not contact_us:
            self._raise_not_found()
        return GetContactUsResponse(**contact_us._mapping)

    async def get_all_contact_us_service(
        self,
        page: int,
        per_page: int,
        order_by: str,
        search: str,
        limit: int,
        offset: int,
        request: Request,
        route_path: str,
    ):
        if not self.repo.valid_order_by(order_by):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "valid order_by choices are: "
                    f"{list(self.repo.VALID_ORDERING_CHOICES.keys())}"
                ),
            )

        total = await self.repo.count_all_contact_us(search)
        contact_us_items = await self.repo.get_all_contact_us_repository(
            limit, offset, order_by, search
        )
        pagination = CustomContactUsPaginationResponse(
            page,
            per_page,
            limit,
            offset,
            request.base_url,
            route_path,
            total,
        )
        return GetAllContactUsResponse(
            count=total,
            next=pagination.the_next(),
            previous=pagination.the_previous(),
            total_pages=pagination.total_pages(),
            current_page=page,
            results=[
                GetContactUsResponse(**item._mapping) for item in contact_us_items
            ],
        )

    async def create_contact_us_service(self, payload: CreateContactUsRequest):
        await self.repo.create_contact_us_repository(payload)
        return JSONResponse(
            content={"message": "New contact-us ticket created successfully"},
            status_code=status.HTTP_201_CREATED,
        )

    async def edit_contact_us_service(
        self,
        contact_us_id: int,
        payload: EditContactUsRequest,
    ):
        await self.repo.edit_contact_us_repository(payload, contact_us_id)
        return JSONResponse(
            content={"message": "Contact-us ticket updated successfully"},
            status_code=status.HTTP_200_OK,
        )

    async def delete_contact_us_service(self, contact_us_id: int):
        await self.repo.delete_contact_us_repository(contact_us_id)
        return JSONResponse(
            content={"message": "Contact-us ticket has been deleted successfully"},
            status_code=status.HTTP_200_OK,
        )

    @staticmethod
    def _raise_not_found():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="We do not have such this contact-us ticket",
        )
