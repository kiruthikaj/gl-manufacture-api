from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.repositories.purchase_order import (
    PurchaseOrderItemRepository,
    PurchaseOrderPaymentRepository,
    PurchaseOrderRepository,
)
from app.schemas.purchase_order import (
    MarkReceivedRequest,
    PurchaseOrderCreate,
    PurchaseOrderDetail,
    PurchaseOrderItemCreate,
    PurchaseOrderItemRead,
    PurchaseOrderItemUpdate,
    PurchaseOrderPaymentCreate,
    PurchaseOrderPaymentRead,
    PurchaseOrderPaymentUpdate,
    PurchaseOrderRead,
    PurchaseOrderUpdate,
)
from app.schemas.responses import MessageResponse, PaginatedResponse, SuccessResponse

router = APIRouter(prefix="/purchase-orders", tags=["Purchase Orders"])


# ─────────────────────────── Purchase Orders ────────────────────────────────

@router.post("/", response_model=SuccessResponse[PurchaseOrderDetail], status_code=201)
def create_purchase_order(payload: PurchaseOrderCreate, db: Session = Depends(get_db)):
    po_repo = PurchaseOrderRepository(db)
    item_repo = PurchaseOrderItemRepository(db)

    order_data = payload.model_dump(exclude={"items"})
    order = po_repo.create(order_data)

    for item in payload.items:
        item_repo.create({"order_id": order.id, **item.model_dump()})

    db.refresh(order)
    return SuccessResponse(data=PurchaseOrderDetail.model_validate(order))


@router.get("/", response_model=PaginatedResponse[PurchaseOrderRead])
def list_purchase_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    repo = PurchaseOrderRepository(db)
    skip = (page - 1) * page_size
    orders = repo.get_all(skip=skip, limit=page_size)
    total = repo.count()
    return PaginatedResponse(
        data=[PurchaseOrderRead.model_validate(o) for o in orders],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/pending", response_model=SuccessResponse[list[PurchaseOrderRead]])
def list_pending_orders(db: Session = Depends(get_db)):
    orders = PurchaseOrderRepository(db).get_pending_delivery()
    return SuccessResponse(data=[PurchaseOrderRead.model_validate(o) for o in orders])


@router.get("/overdue", response_model=SuccessResponse[list[PurchaseOrderRead]])
def list_overdue_orders(
    as_of: date | None = Query(None, description="Cut-off date (defaults to today)"),
    db: Session = Depends(get_db),
):
    orders = PurchaseOrderRepository(db).get_overdue(as_of=as_of)
    return SuccessResponse(data=[PurchaseOrderRead.model_validate(o) for o in orders])


@router.get("/by-date-range", response_model=SuccessResponse[list[PurchaseOrderRead]])
def list_orders_by_date_range(
    start: date = Query(...),
    end: date = Query(...),
    db: Session = Depends(get_db),
):
    orders = PurchaseOrderRepository(db).get_by_order_date_range(start, end)
    return SuccessResponse(data=[PurchaseOrderRead.model_validate(o) for o in orders])


@router.get("/by-supplier/{supplier_id}", response_model=PaginatedResponse[PurchaseOrderRead])
def list_orders_by_supplier(
    supplier_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    repo = PurchaseOrderRepository(db)
    skip = (page - 1) * page_size
    orders = repo.get_by_supplier(supplier_id, skip=skip, limit=page_size)
    return PaginatedResponse(
        data=[PurchaseOrderRead.model_validate(o) for o in orders],
        total=len(orders),
        page=page,
        page_size=page_size,
    )


@router.get("/{order_id}", response_model=SuccessResponse[PurchaseOrderDetail])
def get_purchase_order(order_id: uuid.UUID, db: Session = Depends(get_db)):
    order = PurchaseOrderRepository(db).get_by_id(order_id)
    if not order:
        raise NotFoundException("PurchaseOrder", str(order_id))
    return SuccessResponse(data=PurchaseOrderDetail.model_validate(order))


@router.put("/{order_id}", response_model=SuccessResponse[PurchaseOrderRead])
def update_purchase_order(
    order_id: uuid.UUID, payload: PurchaseOrderUpdate, db: Session = Depends(get_db)
):
    repo = PurchaseOrderRepository(db)
    order = repo.update(order_id, payload.model_dump(exclude_none=True))
    if not order:
        raise NotFoundException("PurchaseOrder", str(order_id))
    return SuccessResponse(data=PurchaseOrderRead.model_validate(order))


@router.delete("/{order_id}", response_model=MessageResponse)
def delete_purchase_order(order_id: uuid.UUID, db: Session = Depends(get_db)):
    deleted = PurchaseOrderRepository(db).delete(order_id)
    if not deleted:
        raise NotFoundException("PurchaseOrder", str(order_id))
    return MessageResponse(message=f"Purchase order {order_id} deleted.")


@router.patch("/{order_id}/mark-received", response_model=SuccessResponse[PurchaseOrderRead])
def mark_order_received(
    order_id: uuid.UUID,
    payload: MarkReceivedRequest,
    db: Session = Depends(get_db),
):
    order = PurchaseOrderRepository(db).mark_received(order_id, payload.received_date)
    if not order:
        raise NotFoundException("PurchaseOrder", str(order_id))
    return SuccessResponse(data=PurchaseOrderRead.model_validate(order))


# ─────────────────────────── Purchase Order Items ───────────────────────────

@router.post(
    "/{order_id}/items",
    response_model=SuccessResponse[PurchaseOrderItemRead],
    status_code=201,
)
def add_order_item(
    order_id: uuid.UUID, payload: PurchaseOrderItemCreate, db: Session = Depends(get_db)
):
    po_repo = PurchaseOrderRepository(db)
    if not po_repo.exists(order_id):
        raise NotFoundException("PurchaseOrder", str(order_id))
    item = PurchaseOrderItemRepository(db).create(
        {"order_id": order_id, **payload.model_dump()}
    )
    return SuccessResponse(data=PurchaseOrderItemRead.model_validate(item))


@router.get(
    "/{order_id}/items",
    response_model=PaginatedResponse[PurchaseOrderItemRead],
)
def list_order_items(
    order_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    po_repo = PurchaseOrderRepository(db)
    if not po_repo.exists(order_id):
        raise NotFoundException("PurchaseOrder", str(order_id))
    skip = (page - 1) * page_size
    items = PurchaseOrderItemRepository(db).get_by_order(
        order_id, skip=skip, limit=page_size
    )
    return PaginatedResponse(
        data=[PurchaseOrderItemRead.model_validate(i) for i in items],
        total=len(items),
        page=page,
        page_size=page_size,
    )


@router.put(
    "/{order_id}/items/{item_id}",
    response_model=SuccessResponse[PurchaseOrderItemRead],
)
def update_order_item(
    order_id: uuid.UUID,
    item_id: uuid.UUID,
    payload: PurchaseOrderItemUpdate,
    db: Session = Depends(get_db),
):
    if not PurchaseOrderRepository(db).exists(order_id):
        raise NotFoundException("PurchaseOrder", str(order_id))
    item_repo = PurchaseOrderItemRepository(db)
    item = item_repo.get_by_id(item_id)
    if not item or item.order_id != order_id:
        raise NotFoundException("PurchaseOrderItem", str(item_id))
    item = item_repo.update(item_id, payload.model_dump(exclude_none=True))
    return SuccessResponse(data=PurchaseOrderItemRead.model_validate(item))


@router.delete("/{order_id}/items/{item_id}", response_model=MessageResponse)
def delete_order_item(
    order_id: uuid.UUID, item_id: uuid.UUID, db: Session = Depends(get_db)
):
    if not PurchaseOrderRepository(db).exists(order_id):
        raise NotFoundException("PurchaseOrder", str(order_id))
    item_repo = PurchaseOrderItemRepository(db)
    item = item_repo.get_by_id(item_id)
    if not item or item.order_id != order_id:
        raise NotFoundException("PurchaseOrderItem", str(item_id))
    item_repo.delete(item_id)
    return MessageResponse(message=f"Item {item_id} removed from order {order_id}.")


# ─────────────────────────── Purchase Order Payments ────────────────────────

@router.post(
    "/{order_id}/payments",
    response_model=SuccessResponse[PurchaseOrderPaymentRead],
    status_code=201,
)
def add_order_payment(
    order_id: uuid.UUID,
    payload: PurchaseOrderPaymentCreate,
    db: Session = Depends(get_db),
):
    if not PurchaseOrderRepository(db).exists(order_id):
        raise NotFoundException("PurchaseOrder", str(order_id))
    payment = PurchaseOrderPaymentRepository(db).create(
        {"order_id": order_id, **payload.model_dump()}
    )
    return SuccessResponse(data=PurchaseOrderPaymentRead.model_validate(payment))


@router.get(
    "/{order_id}/payments",
    response_model=PaginatedResponse[PurchaseOrderPaymentRead],
)
def list_order_payments(
    order_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    if not PurchaseOrderRepository(db).exists(order_id):
        raise NotFoundException("PurchaseOrder", str(order_id))
    skip = (page - 1) * page_size
    payments = PurchaseOrderPaymentRepository(db).get_by_order(
        order_id, skip=skip, limit=page_size
    )
    return PaginatedResponse(
        data=[PurchaseOrderPaymentRead.model_validate(p) for p in payments],
        total=len(payments),
        page=page,
        page_size=page_size,
    )


@router.put(
    "/{order_id}/payments/{payment_id}",
    response_model=SuccessResponse[PurchaseOrderPaymentRead],
)
def update_order_payment(
    order_id: uuid.UUID,
    payment_id: uuid.UUID,
    payload: PurchaseOrderPaymentUpdate,
    db: Session = Depends(get_db),
):
    if not PurchaseOrderRepository(db).exists(order_id):
        raise NotFoundException("PurchaseOrder", str(order_id))
    pay_repo = PurchaseOrderPaymentRepository(db)
    payment = pay_repo.get_by_id(payment_id)
    if not payment or payment.order_id != order_id:
        raise NotFoundException("PurchaseOrderPayment", str(payment_id))
    payment = pay_repo.update(payment_id, payload.model_dump(exclude_none=True))
    return SuccessResponse(data=PurchaseOrderPaymentRead.model_validate(payment))


@router.delete("/{order_id}/payments/{payment_id}", response_model=MessageResponse)
def delete_order_payment(
    order_id: uuid.UUID, payment_id: uuid.UUID, db: Session = Depends(get_db)
):
    if not PurchaseOrderRepository(db).exists(order_id):
        raise NotFoundException("PurchaseOrder", str(order_id))
    pay_repo = PurchaseOrderPaymentRepository(db)
    payment = pay_repo.get_by_id(payment_id)
    if not payment or payment.order_id != order_id:
        raise NotFoundException("PurchaseOrderPayment", str(payment_id))
    pay_repo.delete(payment_id)
    return MessageResponse(message=f"Payment {payment_id} removed from order {order_id}.")
