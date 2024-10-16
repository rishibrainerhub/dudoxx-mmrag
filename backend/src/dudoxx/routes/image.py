from fastapi import APIRouter, File, HTTPException, UploadFile, Depends, status
from fastapi_limiter.depends import RateLimiter

from dudoxx.services.image_service import ImageService
from dudoxx.schemas.image import ImageDescription
from dudoxx.services.api_key_management_service import ApiKeyMiddleware

router = APIRouter()


@router.post("/describe_image", dependencies=[Depends(ApiKeyMiddleware()), Depends(RateLimiter(times=5, seconds=60))])
async def describe_image(
    file: UploadFile = File(...), service: ImageService = Depends(ImageService)
) -> ImageDescription:
    try:
        if file.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG and PNG are accepted.")
        image_description = await service.generate_image_description(file)
        return await service.refine_description_with_langchain(image_description.description)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
