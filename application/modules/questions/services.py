from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

from application.modules.questions.pagination import CustomQuestionPaginationResponse
from application.modules.questions.repository import QuestionRepository
from application.modules.questions.schemas import (
    CreateQuestionRequest,
    EditQuestionRequest,
    GetAllQuestionsResponse,
    GetQuestionResponse,
    PublicGetAllQuestionsResponse,
    PublicQuestionResponse,
)


class QuestionServices:
    def __init__(self, repo: QuestionRepository):
        self.repo = repo

    async def public_get_all_questions_service(self):
        questions = await self.repo.public_get_all_questions_repository()
        return PublicGetAllQuestionsResponse(
            root=[PublicQuestionResponse(**item._mapping) for item in questions]
        )

    async def get_question_service(self, question_id: int):
        question = await self.repo.get_question_repository(question_id)
        if not question:
            self._raise_not_found()
        return GetQuestionResponse(**question._mapping)

    async def get_all_questions_service(
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

        total = await self.repo.count_all_questions(search)
        questions = await self.repo.get_all_questions_repository(
            limit, offset, order_by, search
        )
        pagination = CustomQuestionPaginationResponse(
            page,
            per_page,
            limit,
            offset,
            request.base_url,
            route_path,
            total,
        )
        return GetAllQuestionsResponse(
            count=total,
            next=pagination.the_next(),
            previous=pagination.the_previous(),
            total_pages=pagination.total_pages(),
            current_page=page,
            results=[GetQuestionResponse(**item._mapping) for item in questions],
        )

    async def create_question_service(self, payload: CreateQuestionRequest):
        await self.repo.create_question_repository(payload)
        return JSONResponse(
            content={"message": "New question created successfully"},
            status_code=status.HTTP_201_CREATED,
        )

    async def edit_question_service(
        self,
        question_id: int,
        payload: EditQuestionRequest,
    ):
        await self.repo.edit_question_repository(payload, question_id)
        return JSONResponse(
            content={"message": "Question updated successfully"},
            status_code=status.HTTP_200_OK,
        )

    async def delete_question_service(self, question_id: int):
        await self.repo.delete_question_repository(question_id)
        return JSONResponse(
            content={"message": "Question has been deleted successfully"},
            status_code=status.HTTP_200_OK,
        )

    @staticmethod
    def _raise_not_found():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="We do not have such this question",
        )
