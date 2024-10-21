from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends, HTTPException, Request
import uuid
from fastapi_limiter.depends import RateLimiter

from dudoxx.services.deepgrame_service import DeepgramService
from dudoxx.schemas.deepgram import AudioTaskResponse, AudioTranscriptionResponse
from dudoxx.services.api_key_management_service import ApiKeyMiddleware

router = APIRouter()


@router.post(
    "/transcribe/",
    dependencies=[Depends(ApiKeyMiddleware()), Depends(RateLimiter(times=6, seconds=60))],
)
async def transcribe_audio(
    background_tasks: BackgroundTasks,
    audio: UploadFile = File(...),
    service: DeepgramService = Depends(DeepgramService),
) -> AudioTaskResponse:
    if audio.content_type not in ["audio/wav", "audio/mpeg", "audio/flac"]:
        raise HTTPException(status_code=400, detail="Unsupported file type. Please upload a WAV, MP3, or FLAC file.")
    task_id = str(uuid.uuid4())
    background_tasks.add_task(service.process_transcription, audio, task_id)

    return AudioTaskResponse(task_id=task_id, status="processing")


@router.get("/transcription/{task_id}", dependencies=[Depends(ApiKeyMiddleware())])
async def get_transcription(
    task_id: str, service: DeepgramService = Depends(DeepgramService)
) -> AudioTranscriptionResponse:
    result = await service.get_transcription_result(task_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return AudioTranscriptionResponse(**result)
