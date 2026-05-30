from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.sales_order import SalesOrder, SalesOrderItem
from app.repositories.base import BaseRepository


class SalesOrderRepository(BaseRepository[SalesOrder]):

    def __init__(self, db: Session) -> None:
        super().__init__(SalesOrder, db)

    # ------------------------------------------------------------------ #
    # Lookups                                                              #
    # ------------------------------------------------------------------ #

    def get_by_sales_rep(
        self, sales_rep_id: uuid.UUID, *, skip: int = 0, limit: int = 100
    ) -> list[SalesOrder]:
        """Return all orders owned by a sales rep."""
        stmt = (
            select(SalesOrder)
            .where(SalesOrder.sales_rep_id == sales_rep_id)
            .order_by(SalesOrder.order_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_by_order_date_range(
        self, start: date, end: date
    ) -> list[SalesOrder]:
        """Return orders placed between *start* and *end* (inclusive)."""
        stmt = (
            select(SalesOrder)
            .where(
                SalesOrder.order_date >= start,
                SalesOrder.order_date <= end,
            )
            .order_by(SalesOrder.order_date)
        )
        return list(self.db.scalars(stmt).all())

    def get_overdue(self, as_of: date | None = None) -> list[SalesOrder]:
        """
        Return orders whose due date has passed.
        *as_of* defaults to today.
        """
        cutoff = as_of or date.today()
        stmt = (
            select(SalesOrder)
            .where(
                SalesOrder.due_date.is_not(None),
                SalesOrder.due_date < cutoff,
            )
            .order_by(SalesOrder.due_date)
        )
        return list(self.db.scalars(stmt).all())

    def get_due_on(self, due_date: date) -> list[SalesOrder]:
        """Return all orders due on an exact date."""
        stmt = (
            select(SalesOrder)
            .where(SalesOrder.due_date == due_date)
            .order_by(SalesOrder.order_date)
        )
        return list(self.db.scalars(stmt).all())


class SalesOrderItemRepository(BaseRepository[SalesOrderItem]):

    def __init__(self, db: Session) -> None:
        super().__init__(SalesOrderItem, db)

    def get_by_order(
        self, order_id: uuid.UUID, *, skip: int = 0, limit: int = 100
    ) -> list[SalesOrderItem]:
        """Return all line items for a sales order."""
        stmt = (
            select(SalesOrderItem)
            .where(SalesOrderItem.order_id == order_id)
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_by_product(
        self, product_id: uuid.UUID, *, skip: int = 0, limit: int = 100
    ) -> list[SalesOrderItem]:
        """Return all order lines that reference a specific product."""
        stmt = (
            select(SalesOrderItem)
            .where(SalesOrderItem.product_id == product_id)
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
