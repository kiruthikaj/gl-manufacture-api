import enum
from decimal import Decimal

from sqlalchemy import Enum, ForeignKey, Numeric, String, Text
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

    # Short business code is the natural PK, e.g. "DAI", "GRN"
    raw_category_code: Mapped[str] = mapped_column(String(20), primary_key=True)
    category_name: Mapped[str] = mapped_column(String(50), nullable=False)
    primary_descriptor: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    raw_materials: Mapped[list["RawMaterial"]] = relationship(
        "RawMaterial", back_populates="category"
    )
    suppliers: Mapped[list["Supplier"]] = relationship(
        "Supplier",
        secondary="supplier_raw_material_category",
        back_populates="raw_material_categories",
    )

    def __repr__(self) -> str:
        return (
            f"<RawMaterialCategory code={self.raw_category_code!r} "
            f"name={self.category_name!r}>"
        )


class RawMaterial(Base, TimestampMixin):
    """Master catalog of raw materials used in production."""

    __tablename__ = "raw_materials"

    material_code: Mapped[str] = mapped_column(String(20), primary_key=True)
    category_code: Mapped[str | None] = mapped_column(
        String(20),
        ForeignKey("raw_material_categories.raw_category_code"),
        nullable=True,
    )
    material_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    min_order_qty: Mapped[Decimal | None] = mapped_column(Numeric(12, 3), nullable=True)
    min_required_qty: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 3), nullable=True
    )
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
            f"<RawMaterial material_code={self.material_code} name={self.material_name!r} "
            f"qty={self.available_quantity} {self.unit}>"
        )
