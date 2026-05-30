from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.repositories.base import BaseRepository


class EmployeeRepository(BaseRepository[Employee]):

    def __init__(self, db: Session) -> None:
        super().__init__(Employee, db)

    # ------------------------------------------------------------------ #
    # Lookups                                                              #
    # ------------------------------------------------------------------ #

    def get_by_email(self, email: str) -> Employee | None:
        """Return the employee with this e-mail address, or ``None``."""
        stmt = select(Employee).where(Employee.email == email)
        return self.db.scalars(stmt).first()

    def get_by_role(self, role: str, *, skip: int = 0, limit: int = 100) -> list[Employee]:
        """Return all employees assigned to *role*."""
        stmt = (
            select(Employee)
            .where(Employee.role == role)
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_active(self, *, skip: int = 0, limit: int = 100) -> list[Employee]:
        """Return only active employees."""
        stmt = (
            select(Employee)
            .where(Employee.is_active.is_(True))
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_by_stage(self, stage: str, *, skip: int = 0, limit: int = 100) -> list[Employee]:
        """Return employees at a given stage / grade."""
        stmt = (
            select(Employee)
            .where(Employee.emp_stage == stage)
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
