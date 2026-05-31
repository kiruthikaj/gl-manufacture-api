from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.raw_material import RawMaterial, RawMaterialCategory
from app.repositories.base import BaseRepository


class RawMaterialCategoryRepository(BaseRepository[RawMaterialCategory]):

    def __init__(self, db: Session) -> None:
        super().__init__(RawMaterialCategory, db)

    def get_by_code(self, code: str) -> RawMaterialCategory | None:
        """Exact match on the short business code (e.g. ``"DAI"``)."""
        stmt = select(RawMaterialCategory).where(
            RawMaterialCategory.raw_category_code == code
        )
        return self.db.scalars(stmt).first()

    def get_by_name(self, name: str) -> RawMaterialCategory | None:
        """Exact match on category name."""
        stmt = select(RawMaterialCategory).where(
            RawMaterialCategory.category_name == name
        )
        return self.db.scalars(stmt).first()


class RawMaterialRepository(BaseRepository[RawMaterial]):

    def __init__(self, db: Session) -> None:
        super().__init__(RawMaterial, db)

    # ------------------------------------------------------------------ #
    # Lookups                                                              #
    # ------------------------------------------------------------------ #

    def get_by_name(self, name: str) -> RawMaterial | None:
        """Exact match on material name (unique column)."""
        stmt = select(RawMaterial).where(RawMaterial.material_name == name)
        return self.db.scalars(stmt).first()

    def get_by_name_ilike(
        self, fragment: str, *, skip: int = 0, limit: int = 100
    ) -> list[RawMaterial]:
        """Case-insensitive partial match on material name."""
        stmt = (
            select(RawMaterial)
            .where(RawMaterial.material_name.ilike(f"%{fragment}%"))
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_by_category(
        self, category_code: str, *, skip: int = 0, limit: int = 100
    ) -> list[RawMaterial]:
        """Return all materials belonging to a category."""
        stmt = (
            select(RawMaterial)
            .where(RawMaterial.category_code == category_code)
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_by_unit(
        self, unit: str, *, skip: int = 0, limit: int = 100
    ) -> list[RawMaterial]:
        """Return materials measured in the given unit (e.g. ``"kg"``)."""
        stmt = (
            select(RawMaterial)
            .where(RawMaterial.unit == unit)
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    # ------------------------------------------------------------------ #
    # Stock queries                                                        #
    # ------------------------------------------------------------------ #

    def get_low_stock(self) -> list[RawMaterial]:
        """
        Return materials where ``available_quantity`` has fallen below
        ``min_required_qty`` (both columns must be non-null).
        """
        stmt = select(RawMaterial).where(
            RawMaterial.min_required_qty.is_not(None),
            RawMaterial.available_quantity < RawMaterial.min_required_qty,
        )
        return list(self.db.scalars(stmt).all())

    def exists(self, material_code: str) -> bool:
        """Return True if a raw material with this material_code exists."""
        stmt = select(func.count()).select_from(RawMaterial).where(
            RawMaterial.material_code == material_code
        )
        return (self.db.scalar(stmt) or 0) > 0

    def update_stock(self, material_code: str, quantity: float) -> RawMaterial | None:
        """Directly set ``available_quantity`` for the given material."""
        return self.update(material_code, {"available_quantity": quantity})
