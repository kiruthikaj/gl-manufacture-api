from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.purchase_order import (
    PaymentMode,
    PurchaseOrder,
    PurchaseOrderItem,
    PurchaseOrderPayment,
)
from app.repositories.base import BaseRepository


class PurchaseOrderRepository(BaseRepository[PurchaseOrder]):

    def __init__(self, db: Session) -> None:
        super().__init__(PurchaseOrder, db)

    # ------------------------------------------------------------------ #
    # Lookups                                                              #
    # ------------------------------------------------------------------ #

    def get_by_supplier(
        self, supplier_id: uuid.UUID, *, skip: int = 0, limit: int = 100
    ) -> list[PurchaseOrder]:
        """Return all orders placed with a specific supplier."""
        stmt = (
            select(PurchaseOrder)
            .where(PurchaseOrder.supplier_id == supplier_id)
            .order_by(PurchaseOrder.order_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_by_order_date_range(
        self, start: date, end: date
    ) -> list[PurchaseOrder]:
        """Return orders with an order_date between *start* and *end* (inclusive)."""
        stmt = (
            select(PurchaseOrder)
            .where(
                PurchaseOrder.order_date >= start,
                PurchaseOrder.order_date <= end,
            )
            .order_by(PurchaseOrder.order_date)
        )
        return list(self.db.scalars(stmt).all())

    def get_pending_delivery(self) -> list[PurchaseOrder]:
        """Return orders that have not yet been received (received_date is NULL)."""
        stmt = (
            select(PurchaseOrder)
            .where(PurchaseOrder.received_date.is_(None))
            .order_by(PurchaseOrder.expected_delivery_date)
        )
        return list(self.db.scalars(stmt).all())

    def get_overdue(self, as_of: date | None = None) -> list[PurchaseOrder]:
        """
        Return undelivered orders whose due date has passed.
        *as_of* defaults to today.
        """
        cutoff = as_of or date.today()
        stmt = (
            select(PurchaseOrder)
            .where(
                PurchaseOrder.received_date.is_(None),
                PurchaseOrder.due_date.is_not(None),
                PurchaseOrder.due_date < cutoff,
            )
            .order_by(PurchaseOrder.due_date)
        )
        return list(self.db.scalars(stmt).all())

    def mark_received(
        self, id: uuid.UUID, received_date: date | None = None
    ) -> PurchaseOrder | None:
        """Set ``received_date`` (defaults to today) on the order."""
        return self.update(id, {"received_date": received_date or date.today()})


class PurchaseOrderItemRepository(BaseRepository[PurchaseOrderItem]):

    def __init__(self, db: Session) -> None:
        super().__init__(PurchaseOrderItem, db)

    def get_by_order(
        self, order_id: uuid.UUID, *, skip: int = 0, limit: int = 100
    ) -> list[PurchaseOrderItem]:
        """Return all line items for a purchase order."""
        stmt = (
            select(PurchaseOrderItem)
            .where(PurchaseOrderItem.order_id == order_id)
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_by_material(
        self, material_id: uuid.UUID, *, skip: int = 0, limit: int = 100
    ) -> list[PurchaseOrderItem]:
        """Return all order lines that reference a specific raw material."""
        stmt = (
            select(PurchaseOrderItem)
            .where(PurchaseOrderItem.material_id == material_id)
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def delete_by_order(self, order_id: uuid.UUID) -> int:
        """Delete all line items for an order. Returns number of rows deleted."""
        items = self.get_by_order(order_id, limit=10_000)
        for item in items:
            self.db.delete(item)
        self.db.flush()
        return len(items)


class PurchaseOrderPaymentRepository(BaseRepository[PurchaseOrderPayment]):

    def __init__(self, db: Session) -> None:
        super().__init__(PurchaseOrderPayment, db)

    def get_by_order(
        self, order_id: uuid.UUID, *, skip: int = 0, limit: int = 100
    ) -> list[PurchaseOrderPayment]:
        """Return all payment records for a purchase order."""
        stmt = (
            select(PurchaseOrderPayment)
            .where(PurchaseOrderPayment.order_id == order_id)
            .order_by(PurchaseOrderPayment.payment_date)
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_by_payment_date_range(
        self, start: date, end: date
    ) -> list[PurchaseOrderPayment]:
        """Return payments made between *start* and *end* (inclusive)."""
        stmt = (
            select(PurchaseOrderPayment)
            .where(
                PurchaseOrderPayment.payment_date >= start,
                PurchaseOrderPayment.payment_date <= end,
            )
            .order_by(PurchaseOrderPayment.payment_date)
        )
        return list(self.db.scalars(stmt).all())

    def get_by_mode(
        self, mode: PaymentMode, *, skip: int = 0, limit: int = 100
    ) -> list[PurchaseOrderPayment]:
        """Return payments made via a specific payment mode."""
        stmt = (
            select(PurchaseOrderPayment)
            .where(PurchaseOrderPayment.mode_of_payment == mode)
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
