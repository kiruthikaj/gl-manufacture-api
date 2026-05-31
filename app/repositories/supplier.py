from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.raw_material import RawMaterialCategory
from app.models.supplier import Supplier, SupplierStatus
from app.repositories.base import BaseRepository


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

    def get_by_payment_terms(
        self, terms: str, *, skip: int = 0, limit: int = 100
    ) -> list[Supplier]:
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

    def add_category(
        self, supplier_id: uuid.UUID, raw_category_code: str
    ) -> Supplier | None:
        """Link a raw material category to a supplier. Returns updated supplier."""
        supplier = self.get_by_id(supplier_id)
        category = self.db.get(RawMaterialCategory, raw_category_code)
        if supplier is None or category is None:
            return None
        if category not in supplier.raw_material_categories:
            supplier.raw_material_categories.append(category)
            self.db.flush()
        return supplier

    def remove_category(
        self, supplier_id: uuid.UUID, raw_category_code: str
    ) -> Supplier | None:
        """Unlink a raw material category from a supplier. Returns updated supplier."""
        supplier = self.get_by_id(supplier_id)
        category = self.db.get(RawMaterialCategory, raw_category_code)
        if supplier is None or category is None:
            return None
        if category in supplier.raw_material_categories:
            supplier.raw_material_categories.remove(category)
            self.db.flush()
        return supplier
