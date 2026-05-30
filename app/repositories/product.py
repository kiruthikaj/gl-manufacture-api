from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):

    def __init__(self, db: Session) -> None:
        super().__init__(Product, db)

    # ------------------------------------------------------------------ #
    # Lookups                                                              #
    # ------------------------------------------------------------------ #

    def get_by_code(self, product_code: str) -> Product | None:
        """Exact match on the unique product code (e.g. ``"PRD-0042"``)."""
        stmt = select(Product).where(Product.product_code == product_code)
        return self.db.scalars(stmt).first()

    def get_by_name(self, name: str) -> Product | None:
        """Exact match on product name."""
        stmt = select(Product).where(Product.product_name == name)
        return self.db.scalars(stmt).first()

    def get_by_name_ilike(
        self, fragment: str, *, skip: int = 0, limit: int = 100
    ) -> list[Product]:
        """Case-insensitive partial match on product name."""
        stmt = (
            select(Product)
            .where(Product.product_name.ilike(f"%{fragment}%"))
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_below_min_stock(self) -> list[Product]:
        """
        Return products where ``min_required_qty`` is set (non-null).
        Useful for reorder-trigger reports (actual stock tracking is
        handled upstream; this surfaces the reorder candidates).
        """
        stmt = select(Product).where(Product.min_required_qty.is_not(None))
        return list(self.db.scalars(stmt).all())
