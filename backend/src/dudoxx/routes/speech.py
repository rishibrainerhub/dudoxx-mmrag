# speech_router.py
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import StreamingResponse
import uuid
from fastapi_limiter.depends import RateLimiter

from dudoxx.services.speech_service import SpeechService
from dudoxx.schemas.speech import SpeechRequest, SpeechTaskResponse
from dudoxx.services.api_key_management_service import ApiKeyMiddleware

router = APIRouter()


@router.post("/generate_speech", dependencies=[Depends(ApiKeyMiddleware()), Depends(RateLimiter(times=5, seconds=60))])
async def generate_speech(
    request: SpeechRequest, background_tasks: BackgroundTasks, service: SpeechService = Depends(SpeechService)
) -> SpeechTaskResponse:
    """Initiate speech generation task"""
    task_id = str(uuid.uuid4())

    # Add the generation task to background tasks
    background_tasks.add_task(service.process_speech_generation, request.text, task_id, request.voice)

    return SpeechTaskResponse(task_id=task_id, status="processing", progress=0)


@router.get(
    "/speech_status/{task_id}", dependencies=[Depends(ApiKeyMiddleware()), Depends(RateLimiter(times=5, seconds=60))]
)
async def get_speech_status(task_id: str, service: SpeechService = Depends(SpeechService)) -> SpeechTaskResponse:
    """Check the status of a speech generation task"""
    task_data = await service.cache_service.get(task_id)

    if not task_data:
        raise HTTPException(status_code=404, detail="Task not found")

    return SpeechTaskResponse(task_id=task_id, status=task_data["status"], progress=task_data.get("progress", 0))


@router.get(
    "/download_speech/{task_id}", dependencies=[Depends(ApiKeyMiddleware()), Depends(RateLimiter(times=5, seconds=60))]
)
async def download_speech(task_id: str, service: SpeechService = Depends(SpeechService)):
    """Download the generated speech file"""
    file_path, content_type = await service.get_speech_file(task_id)

    def iterfile():
        with open(file_path, "rb") as f:
            yield from f

    return StreamingResponse(
        iterfile(),
        media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename=speech_{task_id}.mp3"},
    )
