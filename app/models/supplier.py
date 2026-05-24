import enum
import uuid

from sqlalchemy import Boolean, Column, Enum, ForeignKey, String, Table, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class PaymentTerms(str, enum.Enum):
    COD = "COD"          # Cash on Delivery
    ADVANCE = "Advance"
    NET_15 = "Net 15"
    NET_30 = "Net 30"
    NET_45 = "Net 45"
    NET_60 = "Net 60"


class SupplierStatus(str, enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    ON_HOLD = "On Hold"


# Association table — Supplier ↔ SupplyCategory (many-to-many)
supplier_category_association = Table(
    "supplier_category",
    Base.metadata,
    Column(
        "supplier_id",
        Uuid(as_uuid=True),
        ForeignKey("suppliers.id"),
        primary_key=True,
    ),
    Column(
        "category_id",
        Uuid(as_uuid=True),
        ForeignKey("supply_categories.id"),
        primary_key=True,
    ),
)


class SupplyCategory(Base):
    """Lookup table for supply categories (e.g. Dairy, Fruits, Packaging)."""

    __tablename__ = "supply_categories"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    suppliers: Mapped[list["Supplier"]] = relationship(
        "Supplier",
        secondary=supplier_category_association,
        back_populates="supply_categories",
    )

    def __repr__(self) -> str:
        return f"<SupplyCategory id={self.id} name={self.name!r}>"


class Supplier(Base, TimestampMixin):
    """Stores raw-material supplier information."""

    __tablename__ = "suppliers"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Business details
    business_name: Mapped[str] = mapped_column(String(255), nullable=False)
    gst_number: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)

    # Contact details
    contact_person: Mapped[str] = mapped_column(String(150), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)        # primary telephone
    telephone_2: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(254), nullable=True)

    # Address
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Terms & status
    payment_terms: Mapped[PaymentTerms] = mapped_column(
        Enum(PaymentTerms), nullable=False, default=PaymentTerms.NET_30
    )
    status: Mapped[SupplierStatus] = mapped_column(
        Enum(SupplierStatus), nullable=False, default=SupplierStatus.ACTIVE
    )

    # Audit
    created_by: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    updated_by: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)

    # Relationships
    supply_categories: Mapped[list[SupplyCategory]] = relationship(
        "SupplyCategory",
        secondary=supplier_category_association,
        back_populates="suppliers",
    )
    purchase_orders: Mapped[list["PurchaseOrder"]] = relationship(
        "PurchaseOrder", back_populates="supplier"
    )

    def __repr__(self) -> str:
        return f"<Supplier id={self.id} business_name={self.business_name!r}>"
