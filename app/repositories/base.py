"""
Generic base repository.

Every concrete repository inherits from BaseRepository[ModelT] and gets
full CRUD for free.  Domain-specific query methods are added in the
subclass.

Transaction discipline
----------------------
Repositories call ``db.flush()`` so that the new/changed rows are visible
within the *same* session (e.g. the generated PK is populated) without
committing.  The *caller* (service layer or FastAPI route) is responsible
for calling ``db.commit()`` or rolling back on error.
"""

from __future__ import annotations

import uuid
from typing import Any, Generic, Type, TypeVar

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """CRUD operations for a single SQLAlchemy model."""

    def __init__(self, model: Type[ModelT], db: Session) -> None:
        self.model = model
        self.db = db

    # ------------------------------------------------------------------ #
    # Read                                                                 #
    # ------------------------------------------------------------------ #

    def get_by_id(self, id: uuid.UUID) -> ModelT | None:
        """Return the row with the given PK, or ``None`` if not found."""
        return self.db.get(self.model, id)

    def get_all(self, *, skip: int = 0, limit: int = 100) -> list[ModelT]:
        """Return a paginated list of all rows (no filters)."""
        stmt = select(self.model).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def count(self) -> int:
        """Return the total number of rows in the table."""
        stmt = select(func.count()).select_from(self.model)
        return self.db.scalar(stmt) or 0

    def exists(self, id: uuid.UUID) -> bool:
        """Return ``True`` if a row with this PK exists."""
        stmt = select(func.count()).select_from(self.model).where(
            self.model.id == id  # type: ignore[attr-defined]
        )
        return (self.db.scalar(stmt) or 0) > 0

    # ------------------------------------------------------------------ #
    # Write                                                                #
    # ------------------------------------------------------------------ #

    def create(self, data: dict[str, Any]) -> ModelT:
        """
        Instantiate the model from *data*, add it to the session, flush,
        then refresh so that server-side defaults (e.g. ``created_at``)
        are populated before returning.
        """
        obj = self.model(**data)
        self.db.add(obj)
        self.db.flush()
        self.db.refresh(obj)
        return obj

    def update(self, id: uuid.UUID, data: dict[str, Any]) -> ModelT | None:
        """
        Apply *data* (partial or full) to the row identified by *id*.
        Returns the updated instance, or ``None`` if not found.
        ``None`` values in *data* are skipped so that callers may pass
        sparse update payloads.
        """
        obj = self.get_by_id(id)
        if obj is None:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(obj, key, value)
        self.db.flush()
        self.db.refresh(obj)
        return obj

    def delete(self, id: uuid.UUID) -> bool:
        """
        Delete the row identified by *id*.
        Returns ``True`` on success, ``False`` if the row was not found.
        """
        obj = self.get_by_id(id)
        if obj is None:
            return False
        self.db.delete(obj)
        self.db.flush()
        return True
