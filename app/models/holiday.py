import uuid
from datetime import date

from sqlalchemy import Date, Integer, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Holiday(Base):
    """Public / company holidays used to exclude non-working days from scheduling."""

    __tablename__ = "holidays"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # The actual calendar date of the holiday
    leave_date: Mapped[date] = mapped_column(Date, nullable=False, unique=True)
    # Ordinal day-of-year (1–366) — useful for quick range queries
    days_in_year: Mapped[int] = mapped_column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"<Holiday id={self.id} leave_date={self.leave_date}>"
