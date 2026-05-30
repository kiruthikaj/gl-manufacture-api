from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.holiday import Holiday
from app.repositories.base import BaseRepository


class HolidayRepository(BaseRepository[Holiday]):

    def __init__(self, db: Session) -> None:
        super().__init__(Holiday, db)

    # ------------------------------------------------------------------ #
    # Lookups                                                              #
    # ------------------------------------------------------------------ #

    def get_by_date(self, leave_date: date) -> Holiday | None:
        """Return the holiday record for an exact date, or ``None``."""
        stmt = select(Holiday).where(Holiday.leave_date == leave_date)
        return self.db.scalars(stmt).first()

    def get_by_date_range(self, start: date, end: date) -> list[Holiday]:
        """Return all holidays that fall between *start* and *end* (inclusive)."""
        stmt = (
            select(Holiday)
            .where(Holiday.leave_date >= start, Holiday.leave_date <= end)
            .order_by(Holiday.leave_date)
        )
        return list(self.db.scalars(stmt).all())

    def is_holiday(self, check_date: date) -> bool:
        """Return ``True`` if *check_date* is a recorded holiday."""
        return self.get_by_date(check_date) is not None
