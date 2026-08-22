from sqlalchemy import asc, delete, desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from application.modules.questions.models import Question
from application.modules.questions.schemas import (
    CreateQuestionRequest,
    EditQuestionRequest,
)


class QuestionRepository:
    VALID_ORDERING_CHOICES = {
        "id": asc(Question.id),
        "-id": desc(Question.id),
    }

    def __init__(self, session: AsyncSession):
        self.session = session

    async def public_get_all_questions_repository(self):
        result = await self.session.execute(
            select(
                Question.question,
                Question.answer,
                Question.question_place,
            ).order_by(asc(Question.id))
        )
        return result.all()

    async def get_question_repository(self, question_id: int):
        result = await self.session.execute(
            select(
                Question.id,
                Question.question,
                Question.answer,
                Question.question_place,
                Question.created_at,
                Question.updated_at,
            ).where(Question.id == question_id)
        )
        return result.first()

    async def get_all_questions_repository(
        self,
        limit: int,
        offset: int,
        order_by: str,
        search: str,
    ):
        query = (
            select(
                Question.id,
                Question.question,
                Question.answer,
                Question.question_place,
                Question.created_at,
                Question.updated_at,
            )
            .limit(limit)
            .offset(offset)
            .order_by(self.VALID_ORDERING_CHOICES[order_by])
        )
        if search:
            query = query.where(Question.question.ilike(f"%{search}%"))
        result = await self.session.execute(query)
        return result.all()

    async def count_all_questions(self, search: str):
        query = select(func.count(Question.id))
        if search:
            query = query.where(Question.question.ilike(f"%{search}%"))
        result = await self.session.execute(query)
        return result.scalar_one()

    @classmethod
    def valid_order_by(cls, order_by: str):
        return order_by in cls.VALID_ORDERING_CHOICES

    async def create_question_repository(self, payload: CreateQuestionRequest):
        self.session.add(Question(**payload.model_dump()))
        await self.session.commit()

    async def edit_question_repository(
        self,
        payload: EditQuestionRequest,
        question_id: int,
    ):
        data = payload.model_dump(exclude_none=True, exclude_unset=True)
        if not data:
            return
        await self.session.execute(
            update(Question).where(Question.id == question_id).values(**data)
        )
        await self.session.commit()

    async def delete_question_repository(self, question_id: int):
        await self.session.execute(delete(Question).where(Question.id == question_id))
        await self.session.commit()
