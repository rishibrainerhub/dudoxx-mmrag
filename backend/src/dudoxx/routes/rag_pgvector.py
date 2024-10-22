from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from dudoxx.schemas.rag_pgvector import QuestionRequest, QuestionResponse, DocumentResponse
from dudoxx.services.rag_pgvector_service import RAGService
import aiofiles
import os
from fastapi_limiter.depends import RateLimiter

from dudoxx.services.api_key_management_service import ApiKeyMiddleware

router = APIRouter()


@router.post("/documents/upload", dependencies=[Depends(ApiKeyMiddleware()), Depends(RateLimiter(times=5, seconds=60))])
async def upload_document(file: UploadFile = File(...), service: RAGService = Depends(RAGService)) -> DocumentResponse:
    """
    Upload a PDF document for RAG processing.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Save the uploaded file temporarily
    temp_file_path = f"temp/{file.filename}"
    os.makedirs("temp", exist_ok=True)

    try:
        async with aiofiles.open(temp_file_path, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)

        # Process the document
        doc_id = await service.process_document(temp_file_path)

        return DocumentResponse(id=doc_id, status="success", message="Document processed successfully")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@router.post("/rag/question", dependencies=[Depends(ApiKeyMiddleware()), Depends(RateLimiter(times=5, seconds=60))])
async def ask_question(request: QuestionRequest, service: RAGService = Depends(RAGService)) -> QuestionResponse:
    """
    Ask a question using the RAG system.
    """
    try:
        return await service.get_answer(request.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
