from fastapi import Depends, HTTPException, status, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from application.core.database import get_db
from application.modules.collections.services import CollectionServices
from application.modules.collections.repository import CollectionRepository


async def collection_services_dp(
    session: AsyncSession = Depends(get_db),
) -> CollectionServices:
    repo = CollectionRepository(session)
    return CollectionServices(repo)
