from __future__ import annotations

import uuid

from app.core.exceptions import ConflictException, NotFoundException
from app.models.supplier import SupplierStatus
from app.repositories.raw_material import RawMaterialCategoryRepository
from app.repositories.supplier import SupplierRepository
from app.schemas.supplier import (
    SupplierCreate,
    SupplierDetail,
    SupplierRead,
    SupplierUpdate,
)


class SupplierService:
    """Business logic for the supplier domain."""

    def __init__(
        self,
        supplier_repo: SupplierRepository,
        category_repo: RawMaterialCategoryRepository,
    ) -> None:
        self.supplier_repo = supplier_repo
        self.category_repo = category_repo

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def _resolve_categories(self, codes: list[str]):
        """Fetch ORM category objects for the given codes; raise 404 on any unknown code."""
        categories = []
        for code in codes:
            cat = self.category_repo.get_by_id(code)
            if cat is None:
                raise NotFoundException("RawMaterialCategory", code)
            categories.append(cat)
        return categories

    # ------------------------------------------------------------------ #
    # Queries                                                              #
    # ------------------------------------------------------------------ #

    def get(self, supplier_id: uuid.UUID) -> SupplierDetail:
        """Return a single supplier with its linked categories."""
        supplier = self.supplier_repo.get_by_id(supplier_id)
        if not supplier:
            raise NotFoundException("Supplier", str(supplier_id))
        return SupplierDetail.model_validate(supplier)

    def list(
        self,
        *,
        skip: int,
        limit: int,
        status: SupplierStatus | None = None,
        city: str | None = None,
    ) -> tuple[list[SupplierDetail], int]:
        """Return a paginated list of suppliers with categories and optional filters."""
        if status:
            items = self.supplier_repo.get_by_status(status, skip=skip, limit=limit)
            return [SupplierDetail.model_validate(s) for s in items], len(items)
        if city:
            items = self.supplier_repo.get_by_city(city, skip=skip, limit=limit)
            return [SupplierDetail.model_validate(s) for s in items], len(items)
        items = self.supplier_repo.get_all(skip=skip, limit=limit)
        return [SupplierDetail.model_validate(s) for s in items], self.supplier_repo.count()

    def list_active(self, *, skip: int, limit: int) -> tuple[list[SupplierDetail], int]:
        """Return only active suppliers with categories."""
        items = self.supplier_repo.get_active(skip=skip, limit=limit)
        return [SupplierDetail.model_validate(s) for s in items], len(items)

    # ------------------------------------------------------------------ #
    # Mutations                                                            #
    # ------------------------------------------------------------------ #

    def create(self, payload: SupplierCreate) -> SupplierDetail:
        """Create a supplier and link the supplied raw material categories."""
        if payload.gst_number and self.supplier_repo.get_by_gst_number(payload.gst_number):
            raise ConflictException(
                f"Supplier with GST number '{payload.gst_number}' already exists."
            )

        categories = self._resolve_categories(payload.raw_category_codes)

        supplier = self.supplier_repo.create(
            payload.model_dump(exclude={"raw_category_codes"})
        )
        supplier.raw_material_categories = categories
        self.supplier_repo.db.flush()

        return SupplierDetail.model_validate(supplier)

    def update(self, supplier_id: uuid.UUID, payload: SupplierUpdate) -> SupplierDetail:
        """
        Update supplier fields. When ``raw_category_codes`` is provided the
        linked categories are fully replaced with the new list.
        """
        if payload.gst_number:
            existing = self.supplier_repo.get_by_gst_number(payload.gst_number)
            if existing and existing.id != supplier_id:
                raise ConflictException(
                    f"GST number '{payload.gst_number}' is already used by another supplier."
                )

        supplier = self.supplier_repo.update(
            supplier_id,
            payload.model_dump(exclude_none=True, exclude={"raw_category_codes"}),
        )
        if not supplier:
            raise NotFoundException("Supplier", str(supplier_id))

        if payload.raw_category_codes is not None:
            supplier.raw_material_categories = self._resolve_categories(
                payload.raw_category_codes
            )
            self.supplier_repo.db.flush()

        return SupplierDetail.model_validate(supplier)

    def delete(self, supplier_id: uuid.UUID) -> None:
        """Delete a supplier. Raises 404 if not found."""
        if not self.supplier_repo.delete(supplier_id):
            raise NotFoundException("Supplier", str(supplier_id))

    def add_category(
        self, supplier_id: uuid.UUID, raw_category_code: str
    ) -> SupplierDetail:
        """Link one raw material category to a supplier."""
        supplier = self.supplier_repo.get_by_id(supplier_id)
        if not supplier:
            raise NotFoundException("Supplier", str(supplier_id))
        category = self.category_repo.get_by_id(raw_category_code)
        if not category:
            raise NotFoundException("RawMaterialCategory", raw_category_code)
        if category not in supplier.raw_material_categories:
            supplier.raw_material_categories.append(category)
            self.supplier_repo.db.flush()
        return SupplierDetail.model_validate(supplier)

    def remove_category(
        self, supplier_id: uuid.UUID, raw_category_code: str
    ) -> SupplierDetail:
        """Unlink one raw material category from a supplier."""
        supplier = self.supplier_repo.get_by_id(supplier_id)
        if not supplier:
            raise NotFoundException("Supplier", str(supplier_id))
        category = self.category_repo.get_by_id(raw_category_code)
        if not category:
            raise NotFoundException("RawMaterialCategory", raw_category_code)
        if category in supplier.raw_material_categories:
            supplier.raw_material_categories.remove(category)
            self.supplier_repo.db.flush()
        return SupplierDetail.model_validate(supplier)
