from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.raw_material import RawMaterialCategoryRepository
from app.repositories.supplier import SupplierRepository
from app.services.supplier import SupplierService


def get_supplier_repository(db: Session = Depends(get_db)) -> SupplierRepository:
    return SupplierRepository(db)


def get_raw_material_category_repository(
    db: Session = Depends(get_db),
) -> RawMaterialCategoryRepository:
    return RawMaterialCategoryRepository(db)


def get_supplier_service(
    supplier_repo: SupplierRepository = Depends(get_supplier_repository),
    category_repo: RawMaterialCategoryRepository = Depends(
        get_raw_material_category_repository
    ),
) -> SupplierService:
    return SupplierService(supplier_repo, category_repo)
