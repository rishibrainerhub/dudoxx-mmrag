from fastapi import APIRouter, File, UploadFile, HTTPException, Query, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
import uuid
from fastapi_limiter.depends import RateLimiter

from dudoxx.services.transcription_service import TranscriptionService
from dudoxx.schemas.transcription import TranscriptionResponse, TaskResponse
from dudoxx.services.api_key_management_service import ApiKeyMiddleware

router = APIRouter()


@router.post("/transcribe_audio", dependencies=[Depends(ApiKeyMiddleware()), Depends(RateLimiter(times=5, seconds=60))])
async def transcribe_audio(
    background_tasks: BackgroundTasks,
    audio: UploadFile = File(...),
    target_language: str = Query("en", description="ISO 639-1 code for the target language"),
    service: TranscriptionService = Depends(TranscriptionService),
) -> TaskResponse:
    task_id = str(uuid.uuid4())
    await service.cache_service.set(task_id, {"status": "processing"})
    background_tasks.add_task(service.process_audio, audio, target_language, task_id)
    return TaskResponse(
        task_id=task_id,
        status="processing",
        progress=0,
    )


@router.get(
    "/task_status/{task_id}", dependencies=[Depends(ApiKeyMiddleware()), Depends(RateLimiter(times=5, seconds=60))]
)
async def get_task_status(
    task_id: str, service: TranscriptionService = Depends(TranscriptionService)
) -> TranscriptionResponse:
    task = await service.cache_service.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task["status"] == "processing":
        return JSONResponse(content={"status": "processing"})
    elif task["status"] == "failed":
        raise HTTPException(status_code=500, detail=task["error"])
    return TranscriptionResponse(**task)
