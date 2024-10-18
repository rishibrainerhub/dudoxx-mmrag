from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_limiter.depends import RateLimiter

from dudoxx.exceptions.apikey_exceptions import APIKeyError, ApiKeyNotFound, APIKeyRevocationError, APIKeyCreationError
from dudoxx.services.api_key_management_service import APIKeyManagerService, ApiKeyMiddleware
from dudoxx.schemas.api_key import ApiKeyResponse

router = APIRouter()


@router.post("/create_api_key")
async def create_api_key(service: APIKeyManagerService = Depends(APIKeyManagerService)) -> ApiKeyResponse:
    try:
        return await service.create_new_api_key()
    except APIKeyCreationError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/list_keys", dependencies=[Depends(ApiKeyMiddleware()), Depends(RateLimiter(times=5, seconds=60))])
async def list_keys(service: APIKeyManagerService = Depends(APIKeyManagerService)) -> list[ApiKeyResponse]:
    try:
        return await service.list_api_keys()
    except APIKeyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/revoke_key/{api_key}")
async def revoke_key(api_key: str, service: APIKeyManagerService = Depends(APIKeyManagerService)) -> None:
    try:
        await service.revoke_api_key(api_key)
    except ApiKeyNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except APIKeyRevocationError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate_key")
async def validate_key(api_key: str, service: APIKeyManagerService = Depends(APIKeyManagerService)) -> bool:
    try:
        success = await service.validate_api_key(api_key)
        return success
    except APIKeyError as e:
        raise HTTPException(status_code=500, detail=str(e))
