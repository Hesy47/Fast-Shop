from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from application.core.database import get_db
from application.modules.questions.models import Question
from application.modules.questions.repository import QuestionRepository
from application.modules.questions.services import QuestionServices


async def question_services_dp(
    session: AsyncSession = Depends(get_db),
) -> QuestionServices:
    return QuestionServices(QuestionRepository(session))


async def check_question_existence_by_id_dp(
    question_id: int,
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(Question.id).where(Question.id == question_id)
    )
    existing_id = result.scalar_one_or_none()
    if existing_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="We do not have such this question in our database",
        )
    return existing_id
