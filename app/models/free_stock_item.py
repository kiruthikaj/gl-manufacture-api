import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Numeric, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class FreeStockItem(Base):
    """
    Tracks raw-material stock received outside a formal purchase order
    (e.g. samples, returns, bonus stock).  Requires validation before
    being counted toward available inventory.
    """

    __tablename__ = "free_stock_items"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    material_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("raw_materials.id"), nullable=False
    )
    stock_date: Mapped[date] = mapped_column(Date, nullable=False)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    quantity: Mapped[Decimal | None] = mapped_column(Numeric(12, 3), nullable=True)
    # False = pending review; True = accepted into inventory
    to_validate: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Relationships
    raw_material: Mapped["RawMaterial"] = relationship(
        "RawMaterial", back_populates="free_stock_items"
    )

    def __repr__(self) -> str:
        return (
            f"<FreeStockItem id={self.id} material_id={self.material_id} "
            f"qty={self.quantity} validated={self.to_validate}>"
        )
