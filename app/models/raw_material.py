import enum
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Enum, ForeignKey, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class MaterialUnit(str, enum.Enum):
    KG = "kg"
    GRAM = "gram"
    LITRE = "litre"
    ML = "ml"
    PACK = "pack"
    BOX = "box"
    DOZEN = "dozen"
    PIECE = "piece"
    BAG = "bag"
    BARREL = "barrel"


class RawMaterialCategory(Base):
    """
    Classification / grouping for raw materials
    (e.g. Dairy, Grains, Packaging, Chemicals).
    """

    __tablename__ = "raw_material_categories"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # Short business code, e.g. "DAI", "GRN"
    raw_category_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    category_name: Mapped[str] = mapped_column(String(50), nullable=False)
    primary_descriptor: Mapped[str | None] = mapped_column(Text, nullable=True)
    available_qty: Mapped[Decimal | None] = mapped_column(Numeric(12, 3), nullable=True)
    available_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    min_required_qty: Mapped[Decimal | None] = mapped_column(Numeric(12, 3), nullable=True)

    # Relationships
    raw_materials: Mapped[list["RawMaterial"]] = relationship(
        "RawMaterial", back_populates="category"
    )

    def __repr__(self) -> str:
        return (
            f"<RawMaterialCategory id={self.id} "
            f"code={self.raw_category_code!r} name={self.category_name!r}>"
        )


class RawMaterial(Base, TimestampMixin):
    """Master catalog of raw materials used in production."""

    __tablename__ = "raw_materials"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("raw_material_categories.id"),
        nullable=True,
    )
    material_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    min_order_qty: Mapped[Decimal | None] = mapped_column(Numeric(12, 3), nullable=True)
    min_required_qty: Mapped[Decimal | None] = mapped_column(Numeric(12, 3), nullable=True)
    available_quantity: Mapped[Decimal] = mapped_column(
        Numeric(12, 3), nullable=False, default=0
    )
    unit: Mapped[MaterialUnit] = mapped_column(Enum(MaterialUnit), nullable=False)

    # Relationships
    category: Mapped["RawMaterialCategory | None"] = relationship(
        "RawMaterialCategory", back_populates="raw_materials"
    )
    purchase_order_items: Mapped[list["PurchaseOrderItem"]] = relationship(
        "PurchaseOrderItem", back_populates="raw_material"
    )
    free_stock_items: Mapped[list["FreeStockItem"]] = relationship(
        "FreeStockItem", back_populates="raw_material"
    )

    def __repr__(self) -> str:
        return (
            f"<RawMaterial id={self.id} name={self.material_name!r} "
            f"qty={self.available_quantity} {self.unit}>"
        )
