from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from application.core.database import get_db
from application.modules.products.models import Product
from application.modules.products.repository import ProductRepository
from application.modules.products.services import ProductServices


async def product_services_dp(
    session: AsyncSession = Depends(get_db),
) -> ProductServices:
    repo = ProductRepository(session)
    return ProductServices(repo)


async def check_product_existence_by_id_dp(
    product_id: int,
    session: AsyncSession = Depends(get_db),
):
    product_exist_query = select(Product.id).where(Product.id == product_id)
    product_exist_operation = await session.execute(product_exist_query)
    product_exist_result = product_exist_operation.first()

    if not product_exist_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="We do not have such this product in our database",
        )

    return product_exist_result[0]
