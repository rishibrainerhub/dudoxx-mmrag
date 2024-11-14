from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from dudoxx.schemas.rag_pgvector import QuestionRequest, QuestionResponse, DocumentTaskResponse
from dudoxx.services.rag_pgvector_service import RAGService
import aiofiles
import os
from fastapi_limiter.depends import RateLimiter
import uuid
from dudoxx.services.api_key_management_service import ApiKeyMiddleware

router = APIRouter()


@router.post(
    "/documents/upload",
    dependencies=[Depends(ApiKeyMiddleware()), Depends(RateLimiter(times=5, seconds=60))],
    response_model=DocumentTaskResponse,
)
async def upload_document(
    background_tasks: BackgroundTasks, file: UploadFile = File(...), service: RAGService = Depends(RAGService)
) -> DocumentTaskResponse:
    """
    Upload a PDF document for RAG processing.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    temp_file_path = os.path.join("temp", unique_filename)
    os.makedirs("temp", exist_ok=True)

    try:
        async with aiofiles.open(temp_file_path, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)

        task_id = str(uuid.uuid4())

        # Fix: Correct background task syntax and remove extra comma in task_id
        background_tasks.add_task(service.process_document, temp_file_path, task_id)

        # Initialize task status in cache
        await service.cache_service.set(task_id, {"status": "Ingesting", "progress": 0})

        return DocumentTaskResponse(task_id=task_id, status="Ingesting", progress=0)

    except Exception as e:
        # Clean up the file in case of error
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/documents/status/{task_id}", dependencies=[Depends(ApiKeyMiddleware())], response_model=DocumentTaskResponse
)
async def get_document_status(task_id: str, service: RAGService = Depends(RAGService)) -> DocumentTaskResponse:
    """
    Get the status of a document processing task.
    """
    try:
        task_data = await service.cache_service.get(task_id)
        if not task_data:
            raise HTTPException(status_code=404, detail="Task not found")

        return DocumentTaskResponse(task_id=task_id, status=task_data["status"], progress=task_data.get("progress", 0))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rag/question", dependencies=[Depends(ApiKeyMiddleware()), Depends(RateLimiter(times=5, seconds=60))])
async def ask_question(request: QuestionRequest, service: RAGService = Depends(RAGService)) -> QuestionResponse:
    """
    Ask a question using the RAG system.
    """
    try:
        return await service.get_answer(request.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
