from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from fastapi_limiter.depends import RateLimiter

from dudoxx.services.duckduckgo_service import DuckDuckGOService
from dudoxx.services.api_key_management_service import ApiKeyMiddleware
from dudoxx.schemas.duckduckgo import DrugInfo, DiseaseInfo


router = APIRouter()


@router.get(
    "/drug_info/{drug_name}", dependencies=[Depends(ApiKeyMiddleware()), Depends(RateLimiter(times=5, seconds=60))]
)
async def drug_info(
    drug_name: str,
    include_interactions: Optional[bool] = False,
    service: DuckDuckGOService = Depends(DuckDuckGOService),
) -> DrugInfo:
    try:
        return await service.drug_info(drug_name, include_interactions)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/disease_info/{disease_name}",
    dependencies=[Depends(ApiKeyMiddleware()), Depends(RateLimiter(times=5, seconds=60))],
)
async def disease_info(
    disease_name: str,
    include_treatments: Optional[bool] = False,
    service: DuckDuckGOService = Depends(DuckDuckGOService),
) -> DiseaseInfo:
    try:
        return await service.disease_info(disease_name, include_treatments)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
