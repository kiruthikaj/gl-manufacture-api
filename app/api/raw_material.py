from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.repositories.raw_material import RawMaterialCategoryRepository
from app.schemas.raw_material import RawMaterialCategoryRead
from app.schemas.responses import PaginatedResponse, SuccessResponse

router = APIRouter(prefix="/raw-material-categories", tags=["Raw Material Categories"])


@router.get("/", response_model=PaginatedResponse[RawMaterialCategoryRead])
def list_categories(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    repo = RawMaterialCategoryRepository(db)
    skip = (page - 1) * page_size
    categories = repo.get_all(skip=skip, limit=page_size)
    total = repo.count()
    return PaginatedResponse(
        data=[RawMaterialCategoryRead.model_validate(c) for c in categories],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{raw_category_code}", response_model=SuccessResponse[RawMaterialCategoryRead])
def get_category(raw_category_code: str, db: Session = Depends(get_db)):
    category = RawMaterialCategoryRepository(db).get_by_id(raw_category_code)
    if not category:
        raise NotFoundException("RawMaterialCategory", raw_category_code)
    return SuccessResponse(data=RawMaterialCategoryRead.model_validate(category))
