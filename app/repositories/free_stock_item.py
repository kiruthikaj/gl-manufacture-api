from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.free_stock_item import FreeStockItem
from app.repositories.base import BaseRepository


class FreeStockItemRepository(BaseRepository[FreeStockItem]):

    def __init__(self, db: Session) -> None:
        super().__init__(FreeStockItem, db)

    # ------------------------------------------------------------------ #
    # Lookups                                                              #
    # ------------------------------------------------------------------ #

    def get_by_material(
        self, material_id: uuid.UUID, *, skip: int = 0, limit: int = 100
    ) -> list[FreeStockItem]:
        """Return all free-stock entries for a given raw material."""
        stmt = (
            select(FreeStockItem)
            .where(FreeStockItem.material_id == material_id)
            .order_by(FreeStockItem.stock_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_pending_validation(
        self, *, skip: int = 0, limit: int = 100
    ) -> list[FreeStockItem]:
        """Return items that have not yet been validated / accepted."""
        stmt = (
            select(FreeStockItem)
            .where(FreeStockItem.to_validate.is_(False))
            .order_by(FreeStockItem.stock_date)
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_validated(
        self, *, skip: int = 0, limit: int = 100
    ) -> list[FreeStockItem]:
        """Return items that have already been validated."""
        stmt = (
            select(FreeStockItem)
            .where(FreeStockItem.to_validate.is_(True))
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_by_stock_date_range(
        self, start: date, end: date
    ) -> list[FreeStockItem]:
        """Return items with a stock_date between *start* and *end* (inclusive)."""
        stmt = (
            select(FreeStockItem)
            .where(
                FreeStockItem.stock_date >= start,
                FreeStockItem.stock_date <= end,
            )
            .order_by(FreeStockItem.stock_date)
        )
        return list(self.db.scalars(stmt).all())

    def get_expiring_before(self, cutoff: date) -> list[FreeStockItem]:
        """Return non-null expiry items that expire on or before *cutoff*."""
        stmt = (
            select(FreeStockItem)
            .where(
                FreeStockItem.expiry_date.is_not(None),
                FreeStockItem.expiry_date <= cutoff,
            )
            .order_by(FreeStockItem.expiry_date)
        )
        return list(self.db.scalars(stmt).all())

    # ------------------------------------------------------------------ #
    # Validation action                                                    #
    # ------------------------------------------------------------------ #

    def mark_validated(self, id: uuid.UUID) -> FreeStockItem | None:
        """Set ``to_validate = True`` for the given item."""
        return self.update(id, {"to_validate": True})
