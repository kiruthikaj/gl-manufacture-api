from fastapi import APIRouter
from app.schemas.responses import SuccessResponse
from app.core.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=SuccessResponse[dict], summary="Health check")
async def health_check():
    return SuccessResponse(
        data={
            "status": "ok",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
        }
    )
