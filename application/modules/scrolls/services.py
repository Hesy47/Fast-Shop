from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

from application.modules.products.models import ScrollType
from application.modules.scrolls.pagination import CustomScrollPaginationResponse
from application.modules.scrolls.repository import (
    PublicScrollRepository,
    ScrollRepository,
)
from application.modules.scrolls.schemas import (
    CreateScrollRequest,
    EditScrollRequest,
    GetAllScrollsResponse,
    GetScrollResponse,
    PublicGetScrollProductResponse,
    PublicGetScrollProductsResponse,
)
from application.shared.storage import DiskManager


class ScrollServices:
    def __init__(self, repo: ScrollRepository):
        self.repo = repo

    async def get_scroll_service(self, scroll_id: int):
        scroll = await self.repo.get_scroll_repository(scroll_id)
        if not scroll:
            self._raise_not_found()
        return GetScrollResponse(**scroll._mapping)

    async def get_all_scrolls_service(
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

        total = await self.repo.count_all_scrolls(search)
        scrolls = await self.repo.get_all_scrolls_repository(
            limit, offset, order_by, search
        )
        pagination = CustomScrollPaginationResponse(
            page,
            per_page,
            limit,
            offset,
            request.base_url,
            route_path,
            total,
        )
        return GetAllScrollsResponse(
            count=total,
            next=pagination.the_next(),
            previous=pagination.the_previous(),
            total_pages=pagination.total_pages(),
            current_page=page,
            results=[GetScrollResponse(**item._mapping) for item in scrolls],
        )

    async def create_scroll_service(self, payload: CreateScrollRequest):
        self._validate_product_scroll(payload.scroll)
        if await self.repo.check_unique_title_for_create(payload.title):
            self._raise_unique_error("title")
        if await self.repo.check_unique_scroll_for_create(payload.scroll):
            self._raise_unique_error("scroll")

        await self.repo.create_scroll_repository(payload)
        return JSONResponse(
            content={"message": "New scroll created successfully"},
            status_code=status.HTTP_201_CREATED,
        )

    async def edit_scroll_service(
        self,
        scroll_id: int,
        payload: EditScrollRequest,
    ):
        if payload.title and await self.repo.check_unique_title_for_edit(
            payload.title, scroll_id
        ):
            self._raise_unique_error("title")

        if payload.scroll:
            self._validate_product_scroll(payload.scroll)
            if await self.repo.check_unique_scroll_for_edit(
                payload.scroll, scroll_id
            ):
                self._raise_unique_error("scroll")

        await self.repo.edit_scroll_repository(payload, scroll_id)
        return JSONResponse(
            content={"message": "Scroll updated successfully"},
            status_code=status.HTTP_200_OK,
        )

    async def delete_scroll_service(self, scroll_id: int):
        await self.repo.delete_scroll_repository(scroll_id)
        return JSONResponse(
            content={"message": "Scroll has been deleted successfully"},
            status_code=status.HTTP_200_OK,
        )

    @staticmethod
    def _validate_product_scroll(scroll: str):
        try:
            return ScrollType(scroll)
        except ValueError:
            valid_values = [item.value for item in ScrollType]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "field": "scroll",
                    "status": status.HTTP_400_BAD_REQUEST,
                    "type": "value_error",
                    "error": f"Valid scroll choices are: {valid_values}",
                },
            )

    @staticmethod
    def _raise_unique_error(field: str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "field": field,
                "status": status.HTTP_400_BAD_REQUEST,
                "type": "value_error",
                "error": f"This {field} is already taken",
            },
        )

    @staticmethod
    def _raise_not_found():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="We do not have such this scroll",
        )


class PublicScrollServices:
    def __init__(self, repo: PublicScrollRepository):
        self.repo = repo

    async def get_scroll_products_service(
        self,
        scroll: str,
        request: Request,
    ):
        normalized_scroll = self.normalize_scroll_name(scroll)
        scroll_data = await self.repo.get_public_scroll_repository(normalized_scroll)
        if scroll_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="We do not have such this scroll",
            )

        product_scroll = ScrollServices._validate_product_scroll(normalized_scroll)
        products = await self.repo.get_products_repository(product_scroll)
        return PublicGetScrollProductsResponse(
            title=scroll_data.title,
            scroll=scroll_data.scroll,
            link=scroll_data.link,
            query=scroll_data.query,
            products=[self._build_product_response(item, request) for item in products],
        )

    @staticmethod
    def normalize_scroll_name(scroll: str):
        return scroll.strip().lower().replace("-", "_")

    @staticmethod
    def _calculate_discount_percent(price: int, discounted_price: int) -> str:
        if price == 0:
            return "0 %"
        discount_percent = int((price - discounted_price) / price * 100)
        return f"{discount_percent} %"

    @classmethod
    def _build_product_response(cls, product: object, request: Request):
        return PublicGetScrollProductResponse(
            id=product.id,
            title=product.title,
            price=product.price,
            discounted_price=product.discounted_price,
            discount_percent=cls._calculate_discount_percent(
                product.price, product.discounted_price
            ),
            status=product.status,
            menu=product.menu,
            scroll=product.scroll,
            slug_tag=product.slug_tag,
            title_tag=product.title_tag,
            description_tag=product.description_tag,
            gallery_set=[
                {
                    "id": image.id,
                    "image": (
                        f"{request.base_url}"
                        f"{DiskManager.PRODUCTS_SAVE_PATH}"
                        f"{image.image}"
                    ),
                }
                for image in sorted(product.images, key=lambda image: image.id)
            ],
        )
