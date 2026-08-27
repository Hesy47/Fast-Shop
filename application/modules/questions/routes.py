from fastapi import APIRouter, Depends, Request

from application.core.permissions import CustomPermissions
from application.modules.questions.dependencies import (
    check_question_existence_by_id_dp,
    question_services_dp,
)
from application.modules.questions.pagination import CustomQuestionPaginationParams
from application.modules.questions.schemas import (
    CreateQuestionRequest,
    EditQuestionRequest,
    PublicGetAllQuestionsResponse,
)
from application.modules.questions.services import QuestionServices

question_router = APIRouter(prefix="/api")


@question_router.get(
    path="/questions",
    tags=["Question-Public"],
    response_model=PublicGetAllQuestionsResponse,
)
async def public_get_all_questions(
    service: QuestionServices = Depends(question_services_dp),
):
    return await service.public_get_all_questions_service()


@question_router.get(
    path="/get-question/{question_id:int}",
    tags=["Question-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def get_question(
    question_id: int,
    service: QuestionServices = Depends(question_services_dp),
):
    return await service.get_question_service(question_id)


@question_router.get(
    path="/get-all-questions",
    tags=["Question-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def get_all_questions(
    request: Request,
    params: CustomQuestionPaginationParams = Depends(),
    service: QuestionServices = Depends(question_services_dp),
):
    return await service.get_all_questions_service(
        params.page,
        params.per_page,
        params.ordering,
        params.search,
        params.limit,
        params.offset,
        request,
        "api/get-all-questions",
    )


@question_router.post(
    path="/create-question",
    tags=["Question-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def create_question(
    payload: CreateQuestionRequest,
    service: QuestionServices = Depends(question_services_dp),
):
    return await service.create_question_service(payload)


@question_router.patch(
    path="/edit-question/{question_id:int}",
    tags=["Question-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def edit_question(
    payload: EditQuestionRequest,
    question_id: int = Depends(check_question_existence_by_id_dp),
    service: QuestionServices = Depends(question_services_dp),
):
    return await service.edit_question_service(question_id, payload)


@question_router.delete(
    path="/delete-question/{question_id:int}",
    tags=["Question-Administration"],
    dependencies=[Depends(CustomPermissions.is_admin)],
)
async def delete_question(
    question_id: int = Depends(check_question_existence_by_id_dp),
    service: QuestionServices = Depends(question_services_dp),
):
    return await service.delete_question_service(question_id)
