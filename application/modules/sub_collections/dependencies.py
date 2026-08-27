from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from application.core.database import get_db
from application.modules.sub_collections.services import SubCollectionServices
from application.modules.sub_collections.repository import SubCollectionRepository
from application.modules.sub_collections.models import SubCollection


async def sub_collection_services_dp(
    session: AsyncSession = Depends(get_db),
) -> SubCollectionServices:
    repo = SubCollectionRepository(session)
    return SubCollectionServices(repo)


async def check_sub_collection_existence_by_id_dp(
    sub_collection_id: int, session: AsyncSession = Depends(get_db)
):
    sub_collection_exist_query = select(SubCollection.id).where(
        SubCollection.id == sub_collection_id
    )
    sub_collection_exist_operation = await session.execute(sub_collection_exist_query)
    sub_collection_exist_result = sub_collection_exist_operation.first()

    if not sub_collection_exist_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="we do not have such this sub collection in our database",
        )

    return sub_collection_exist_result[0]
