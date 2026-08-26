from sqlalchemy import and_, asc, delete, desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, load_only, selectinload

from application.modules.collections.models import Collection
from application.modules.products.models import (
    Product,
    ProductImage,
    ScrollType,
)
from application.modules.scrolls.models import Scroll
from application.modules.scrolls.schemas import CreateScrollRequest, EditScrollRequest


class ScrollRepository:
    VALID_ORDERING_CHOICES = {
        "id": asc(Scroll.id),
        "-id": desc(Scroll.id),
    }

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_scroll_repository(self, scroll_id: int):
        query = select(
            Scroll.id,
            Scroll.title,
            Scroll.scroll,
            Scroll.link,
            Scroll.query,
            Scroll.created_at,
            Scroll.updated_at,
        ).where(Scroll.id == scroll_id)
        result = await self.session.execute(query)
        return result.first()

    async def get_all_scrolls_repository(
        self,
        limit: int,
        offset: int,
        order_by: str,
        search: str,
    ):
        query = (
            select(
                Scroll.id,
                Scroll.title,
                Scroll.scroll,
                Scroll.link,
                Scroll.query,
                Scroll.created_at,
                Scroll.updated_at,
            )
            .limit(limit)
            .offset(offset)
            .order_by(self.VALID_ORDERING_CHOICES[order_by])
        )
        if search:
            query = query.where(Scroll.title.ilike(f"%{search}%"))
        result = await self.session.execute(query)
        return result.all()

    async def count_all_scrolls(self, search: str):
        query = select(func.count(Scroll.id))
        if search:
            query = query.where(Scroll.title.ilike(f"%{search}%"))
        result = await self.session.execute(query)
        return result.scalar_one()

    @classmethod
    def valid_order_by(cls, order_by: str):
        return order_by in cls.VALID_ORDERING_CHOICES

    async def check_unique_title_for_create(self, title: str):
        result = await self.session.execute(
            select(Scroll.id).where(Scroll.title == title)
        )
        return result.first()

    async def check_unique_scroll_for_create(self, scroll: str):
        result = await self.session.execute(
            select(Scroll.id).where(Scroll.scroll == scroll)
        )
        return result.first()

    async def create_scroll_repository(self, payload: CreateScrollRequest):
        self.session.add(Scroll(**payload.model_dump()))
        await self.session.commit()

    async def check_unique_title_for_edit(self, title: str, scroll_id: int):
        result = await self.session.execute(
            select(Scroll.id).where(
                and_(Scroll.title == title, Scroll.id != scroll_id)
            )
        )
        return result.first()

    async def check_unique_scroll_for_edit(self, scroll: str, scroll_id: int):
        result = await self.session.execute(
            select(Scroll.id).where(
                and_(Scroll.scroll == scroll, Scroll.id != scroll_id)
            )
        )
        return result.first()

    async def edit_scroll_repository(
        self,
        payload: EditScrollRequest,
        scroll_id: int,
    ):
        data = payload.model_dump(exclude_none=True, exclude_unset=True)
        if not data:
            return
        await self.session.execute(
            update(Scroll).where(Scroll.id == scroll_id).values(**data)
        )
        await self.session.commit()

    async def delete_scroll_repository(self, scroll_id: int):
        await self.session.execute(delete(Scroll).where(Scroll.id == scroll_id))
        await self.session.commit()


class PublicScrollRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_public_scroll_repository(self, scroll: str):
        result = await self.session.execute(
            select(
                Scroll.title,
                Scroll.scroll,
                Scroll.link,
                Scroll.query,
            ).where(Scroll.scroll == scroll)
        )
        return result.first()

    @staticmethod
    def _with_related_data(query):
        return query.options(
            load_only(
                Product.id,
                Product.title,
                Product.price,
                Product.discounted_price,
                Product.status,
                Product.menu,
                Product.scroll,
                Product.slug_tag,
                Product.title_tag,
                Product.description_tag,
                Product.collection_id,
            ),
            joinedload(Product.collection, innerjoin=True).load_only(
                Collection.title,
            ),
            selectinload(Product.images).load_only(
                ProductImage.id,
                ProductImage.image,
            ),
        )

    async def get_products_repository(
        self,
        scroll: ScrollType,
    ):
        query = self._with_related_data(
            select(Product)
            .where(Product.scroll == scroll)
            .order_by(desc(Product.id))
        )
        result = await self.session.execute(query)
        return result.scalars().all()
