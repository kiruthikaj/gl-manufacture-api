from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_supplier_service
from app.models.supplier import SupplierStatus
from app.schemas.responses import MessageResponse, PaginatedResponse, SuccessResponse
from app.schemas.supplier import SupplierCreate, SupplierDetail, SupplierUpdate
from app.services.supplier import SupplierService

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


# ─────────────────────────── CRUD ───────────────────────────────────────────

@router.post("/", response_model=SuccessResponse[SupplierDetail], status_code=201)
def create_supplier(
    payload: SupplierCreate,
    service: SupplierService = Depends(get_supplier_service),
):
    return SuccessResponse(data=service.create(payload))


@router.get("/", response_model=PaginatedResponse[SupplierDetail])
def list_suppliers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: SupplierStatus | None = Query(None),
    city: str | None = Query(None),
    service: SupplierService = Depends(get_supplier_service),
):
    skip = (page - 1) * page_size
    items, total = service.list(skip=skip, limit=page_size, status=status, city=city)
    return PaginatedResponse(data=items, total=total, page=page, page_size=page_size)


@router.get("/active", response_model=PaginatedResponse[SupplierDetail])
def list_active_suppliers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: SupplierService = Depends(get_supplier_service),
):
    skip = (page - 1) * page_size
    items, total = service.list_active(skip=skip, limit=page_size)
    return PaginatedResponse(data=items, total=total, page=page, page_size=page_size)


@router.get("/{supplier_id}", response_model=SuccessResponse[SupplierDetail])
def get_supplier(
    supplier_id: uuid.UUID,
    service: SupplierService = Depends(get_supplier_service),
):
    return SuccessResponse(data=service.get(supplier_id))


@router.put("/{supplier_id}", response_model=SuccessResponse[SupplierDetail])
def update_supplier(
    supplier_id: uuid.UUID,
    payload: SupplierUpdate,
    service: SupplierService = Depends(get_supplier_service),
):
    return SuccessResponse(data=service.update(supplier_id, payload))


@router.delete("/{supplier_id}", response_model=MessageResponse)
def delete_supplier(
    supplier_id: uuid.UUID,
    service: SupplierService = Depends(get_supplier_service),
):
    service.delete(supplier_id)
    return MessageResponse(message=f"Supplier {supplier_id} deleted.")


# ─────────────────────────── Category management ────────────────────────────

@router.put(
    "/{supplier_id}/categories/{raw_category_code}",
    response_model=SuccessResponse[SupplierDetail],
)
def add_category(
    supplier_id: uuid.UUID,
    raw_category_code: str,
    service: SupplierService = Depends(get_supplier_service),
):
    return SuccessResponse(data=service.add_category(supplier_id, raw_category_code))


@router.delete(
    "/{supplier_id}/categories/{raw_category_code}",
    response_model=SuccessResponse[SupplierDetail],
)
def remove_category(
    supplier_id: uuid.UUID,
    raw_category_code: str,
    service: SupplierService = Depends(get_supplier_service),
):
    return SuccessResponse(data=service.remove_category(supplier_id, raw_category_code))
