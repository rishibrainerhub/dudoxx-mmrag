from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks, Header
from dudoxx.schemas.rag_pgvector import QuestionRequest, QuestionResponse, DocumentTaskResponse
from dudoxx.services.rag_pgvector_service import RAGService
import aiofiles
import os
from fastapi_limiter.depends import RateLimiter
import uuid
from dudoxx.services.api_key_management_service import ApiKeyMiddleware
from typing import Optional

router = APIRouter()


async def get_context_id(x_context_id: Optional[str] = Header(None)) -> Optional[str]:
    """
    Dependency to extract context ID from headers.
    You can modify this to get context from wherever makes sense for your application
    (e.g., JWT tokens, query parameters, etc.)
    """
    return x_context_id


async def get_rag_service(context_id: str = Depends(get_context_id)) -> RAGService:
    """
    Dependency to get RAG service with context.
    """
    return RAGService(default_context_id=context_id)


@router.post(
    "/documents/upload",
    dependencies=[Depends(ApiKeyMiddleware()), Depends(RateLimiter(times=5, seconds=60))],
    response_model=DocumentTaskResponse,
)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    context_id: str = Depends(get_context_id),
    service: RAGService = Depends(get_rag_service),
) -> DocumentTaskResponse:
    """
    Upload a PDF document for RAG processing within a specific context.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    if not context_id:
        raise HTTPException(status_code=400, detail="Context ID is required for document upload")

    unique_filename = f"{context_id}_{uuid.uuid4()}_{file.filename}"
    temp_file_path = os.path.join("temp", unique_filename)
    os.makedirs("temp", exist_ok=True)

    try:
        async with aiofiles.open(temp_file_path, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)

        task_id = str(uuid.uuid4())

        # Add context_id to the background task
        background_tasks.add_task(service.process_document, temp_file_path, task_id, context_id)

        # Initialize task status in cache with context information
        await service.cache_service.set(task_id, {"status": "Ingesting", "progress": 0, "context_id": context_id})

        return DocumentTaskResponse(task_id=task_id, status="Ingesting", progress=0, context_id=context_id)

    except Exception as e:
        # Clean up the file in case of error
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/documents/status/{task_id}", dependencies=[Depends(ApiKeyMiddleware())], response_model=DocumentTaskResponse
)
async def get_document_status(
    task_id: str, context_id: str = Depends(get_context_id), service: RAGService = Depends(get_rag_service)
) -> DocumentTaskResponse:
    """
    Get the status of a document processing task within a context.
    """
    try:
        task_data = await service.cache_service.get(task_id)
        if not task_data:
            raise HTTPException(status_code=404, detail="Task not found")

        # # Verify context matches
        # if task_data.get("context_id") != context_id:
        #     raise HTTPException(
        #         status_code=403,
        #         detail="Access denied: Context mismatch"
        #     )

        return DocumentTaskResponse(
            task_id=task_id, status=task_data["status"], progress=task_data.get("progress", 0), context_id=context_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rag/question", dependencies=[Depends(ApiKeyMiddleware()), Depends(RateLimiter(times=5, seconds=60))])
async def ask_question(
    request: QuestionRequest, context_id: str = Depends(get_context_id), service: RAGService = Depends(get_rag_service)
) -> QuestionResponse:
    """
    Ask a question using the RAG system within a specific context.
    """
    try:
        return await service.get_answer(question=request.question, context_id=context_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/context/{context_id}", dependencies=[Depends(ApiKeyMiddleware())])
async def delete_context(context_id: str, service: RAGService = Depends(get_rag_service)) -> dict:
    """
    Delete all documents and embeddings for a specific context.
    """
    try:
        await service.delete_context(context_id)
        return {"message": f"Successfully deleted context: {context_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
