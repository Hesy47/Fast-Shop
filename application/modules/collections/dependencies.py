from fastapi import Depends, HTTPException, status, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from application.core.database import get_db
from application.modules.collections.services import CollectionServices
from application.modules.collections.repository import CollectionRepository
from application.modules.collections.models import Collection


async def collection_services_dp(
    session: AsyncSession = Depends(get_db),
) -> CollectionServices:
    repo = CollectionRepository(session)
    return CollectionServices(repo)


async def check_collection_existence_by_id_dp(
    collection_id: int, session: AsyncSession = Depends(get_db)
):
    collection_exist_query = select(Collection.id).where(Collection.id == collection_id)
    collection_exist_operation = await session.execute(collection_exist_query)
    collection_exist_result = collection_exist_operation.first()

    if not collection_exist_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="we do not have such this collection in our database",
        )

    return collection_exist_result[0]
