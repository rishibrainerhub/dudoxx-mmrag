from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_limiter.depends import RateLimiter

from dudoxx.services.rag_service import RAGService, RAGServiceError
from dudoxx.schemas.rag import Query, EnhancedAnswer, StructuredAnswer
from dudoxx.services.api_key_management_service import ApiKeyMiddleware

router = APIRouter()


@router.post("/search", dependencies=[Depends(ApiKeyMiddleware()), Depends(RateLimiter(times=5, seconds=60))])
async def search(query: Query, service: RAGService = Depends(RAGService)) -> dict:
    try:
        await service.search_and_store(query.text)
        return {"message": "Search completed and results stored successfully"}
    except RAGServiceError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/answer", dependencies=[Depends(ApiKeyMiddleware()), Depends(RateLimiter(times=5, seconds=60))])
async def get_answer(query: Query, service: RAGService = Depends(RAGService)) -> EnhancedAnswer:
    try:
        structured_answer: StructuredAnswer = await service.get_answer(query.text)
        return EnhancedAnswer(
            content=structured_answer.answer, sources=structured_answer.sources, confidence=structured_answer.confidence
        )
    except RAGServiceError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/conversational_answer", dependencies=[Depends(ApiKeyMiddleware()), Depends(RateLimiter(times=5, seconds=60))]
)
async def get_conversational_answer(query: Query, service: RAGService = Depends(RAGService)) -> EnhancedAnswer:
    try:
        response = await service.get_conversational_answer(query.text)
        return EnhancedAnswer(
            content=response["answer"], sources=response["sources"], confidence=response["confidence"]
        )
    except RAGServiceError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
