from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.sales_rep import SalesRep
from app.repositories.base import BaseRepository


class SalesRepRepository(BaseRepository[SalesRep]):

    def __init__(self, db: Session) -> None:
        super().__init__(SalesRep, db)

    # ------------------------------------------------------------------ #
    # Lookups                                                              #
    # ------------------------------------------------------------------ #

    def get_by_name(self, name: str) -> SalesRep | None:
        """Exact match on rep name."""
        stmt = select(SalesRep).where(SalesRep.name == name)
        return self.db.scalars(stmt).first()

    def get_by_name_ilike(
        self, fragment: str, *, skip: int = 0, limit: int = 100
    ) -> list[SalesRep]:
        """Case-insensitive partial match on name."""
        stmt = (
            select(SalesRep)
            .where(SalesRep.name.ilike(f"%{fragment}%"))
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_active(self, *, skip: int = 0, limit: int = 100) -> list[SalesRep]:
        """Return only active sales reps."""
        stmt = (
            select(SalesRep)
            .where(SalesRep.is_active.is_(True))
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_by_city(
        self, city: str, *, skip: int = 0, limit: int = 100
    ) -> list[SalesRep]:
        """Return reps located in *city* (case-insensitive)."""
        stmt = (
            select(SalesRep)
            .where(SalesRep.city.ilike(city))
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_by_state(
        self, state: str, *, skip: int = 0, limit: int = 100
    ) -> list[SalesRep]:
        """Return reps located in *state* (case-insensitive)."""
        stmt = (
            select(SalesRep)
            .where(SalesRep.state.ilike(state))
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
