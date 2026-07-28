from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from application.core.database import get_db
from application.modules.products.models import Product, ProductImage, ProductInformation
from application.modules.products.repository import (
    ProductImageRepository,
    ProductInformationRepository,
    ProductRepository,
)
from application.modules.products.services import (
    ProductImageServices,
    ProductInformationServices,
    ProductServices,
)


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


async def product_image_services_dp(
    session: AsyncSession = Depends(get_db),
) -> ProductImageServices:
    repo = ProductImageRepository(session)
    return ProductImageServices(repo)


async def check_product_image_existence_by_id_dp(
    product_image_id: int,
    session: AsyncSession = Depends(get_db),
):
    existence_query = select(ProductImage.id).where(
        ProductImage.id == product_image_id
    )
    existence_operation = await session.execute(existence_query)
    existence_result = existence_operation.first()

    if not existence_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="We do not have such this product image in our database",
        )

    return existence_result[0]


async def product_information_services_dp(
    session: AsyncSession = Depends(get_db),
) -> ProductInformationServices:
    repo = ProductInformationRepository(session)
    return ProductInformationServices(repo)


async def check_product_information_existence_by_id_dp(
    product_information_id: int,
    session: AsyncSession = Depends(get_db),
):
    existence_query = select(ProductInformation.id).where(
        ProductInformation.id == product_information_id
    )
    existence_operation = await session.execute(existence_query)
    existence_result = existence_operation.first()

    if not existence_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="We do not have such this product information in our database",
        )

    return existence_result[0]
