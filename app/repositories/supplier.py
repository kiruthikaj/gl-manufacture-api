from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.supplier import Supplier, SupplierStatus, SupplyCategory
from app.repositories.base import BaseRepository


class SupplyCategoryRepository(BaseRepository[SupplyCategory]):

    def __init__(self, db: Session) -> None:
        super().__init__(SupplyCategory, db)

    def get_by_name(self, name: str) -> SupplyCategory | None:
        """Return the category whose name matches exactly, or ``None``."""
        stmt = select(SupplyCategory).where(SupplyCategory.name == name)
        return self.db.scalars(stmt).first()

    def get_by_name_ilike(self, fragment: str, *, skip: int = 0, limit: int = 100) -> list[SupplyCategory]:
        """Case-insensitive partial match on category name."""
        stmt = (
            select(SupplyCategory)
            .where(SupplyCategory.name.ilike(f"%{fragment}%"))
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())


class SupplierRepository(BaseRepository[Supplier]):

    def __init__(self, db: Session) -> None:
        super().__init__(Supplier, db)

    # ------------------------------------------------------------------ #
    # Lookups                                                              #
    # ------------------------------------------------------------------ #

    def get_by_business_name(self, name: str) -> Supplier | None:
        """Exact match on business name."""
        stmt = select(Supplier).where(Supplier.business_name == name)
        return self.db.scalars(stmt).first()

    def get_by_gst_number(self, gst: str) -> Supplier | None:
        """Exact match on GST number (unique column)."""
        stmt = select(Supplier).where(Supplier.gst_number == gst)
        return self.db.scalars(stmt).first()

    def get_by_status(
        self, status: SupplierStatus, *, skip: int = 0, limit: int = 100
    ) -> list[Supplier]:
        """Return suppliers filtered by status (Active / Inactive / On Hold)."""
        stmt = (
            select(Supplier)
            .where(Supplier.status == status)
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_active(self, *, skip: int = 0, limit: int = 100) -> list[Supplier]:
        """Shortcut — return only active suppliers."""
        return self.get_by_status(SupplierStatus.ACTIVE, skip=skip, limit=limit)

    def get_by_city(self, city: str, *, skip: int = 0, limit: int = 100) -> list[Supplier]:
        """Return suppliers located in *city* (case-insensitive)."""
        stmt = (
            select(Supplier)
            .where(Supplier.city.ilike(city))
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_by_payment_terms(self, terms: str, *, skip: int = 0, limit: int = 100) -> list[Supplier]:
        """Return suppliers who operate under the given payment terms."""
        stmt = (
            select(Supplier)
            .where(Supplier.payment_terms == terms)
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    # ------------------------------------------------------------------ #
    # Many-to-many helpers                                                 #
    # ------------------------------------------------------------------ #

    def add_category(self, supplier_id: uuid.UUID, category_id: uuid.UUID) -> Supplier | None:
        """Link a supply category to a supplier. Returns updated supplier."""
        supplier = self.get_by_id(supplier_id)
        category = self.db.get(SupplyCategory, category_id)
        if supplier is None or category is None:
            return None
        if category not in supplier.supply_categories:
            supplier.supply_categories.append(category)
            self.db.flush()
        return supplier

    def remove_category(self, supplier_id: uuid.UUID, category_id: uuid.UUID) -> Supplier | None:
        """Unlink a supply category from a supplier. Returns updated supplier."""
        supplier = self.get_by_id(supplier_id)
        category = self.db.get(SupplyCategory, category_id)
        if supplier is None or category is None:
            return None
        if category in supplier.supply_categories:
            supplier.supply_categories.remove(category)
            self.db.flush()
        return supplier
