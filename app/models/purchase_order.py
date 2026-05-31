import enum
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Enum, ForeignKey, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class PaymentMode(str, enum.Enum):
    CASH = "Cash"
    BANK_TRANSFER = "Bank Transfer"
    CHEQUE = "Cheque"
    UPI = "UPI"
    CREDIT = "Credit"


class PurchaseOrder(Base):
    """Header record for an order placed with a supplier."""

    __tablename__ = "purchase_orders"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    supplier_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("suppliers.id"), nullable=False
    )
    order_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expected_delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    received_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Relationships
    supplier: Mapped["Supplier"] = relationship(
        "Supplier", back_populates="purchase_orders"
    )
    items: Mapped[list["PurchaseOrderItem"]] = relationship(
        "PurchaseOrderItem",
        back_populates="purchase_order",
        cascade="all, delete-orphan",
    )
    payments: Mapped[list["PurchaseOrderPayment"]] = relationship(
        "PurchaseOrderPayment",
        back_populates="purchase_order",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<PurchaseOrder id={self.id} supplier_id={self.supplier_id} "
            f"order_date={self.order_date}>"
        )


class PurchaseOrderItem(Base):
    """Raw-material line items within a purchase order."""

    __tablename__ = "purchase_order_items"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("purchase_orders.id"), nullable=False
    )
    material_id: Mapped[str] = mapped_column(
        String(20), ForeignKey("raw_materials.material_code"), nullable=False
    )
    quantity: Mapped[Decimal | None] = mapped_column(Numeric(12, 3), nullable=True)
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    # Effective rate after discounts / negotiations
    rate: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)

    # Relationships
    purchase_order: Mapped["PurchaseOrder"] = relationship(
        "PurchaseOrder", back_populates="items"
    )
    raw_material: Mapped["RawMaterial"] = relationship(
        "RawMaterial", back_populates="purchase_order_items"
    )

    def __repr__(self) -> str:
        return (
            f"<PurchaseOrderItem id={self.id} order_id={self.order_id} "
            f"material_id={self.material_id} qty={self.quantity}>"
        )


class PurchaseOrderPayment(Base):
    """Payment instalments made against a purchase order."""

    __tablename__ = "purchase_order_payments"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("purchase_orders.id"), nullable=False
    )
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    mode_of_payment: Mapped[PaymentMode | None] = mapped_column(
        Enum(PaymentMode), nullable=True
    )
    # Reference label / cheque number / transaction ID
    payment_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    purchase_order: Mapped["PurchaseOrder"] = relationship(
        "PurchaseOrder", back_populates="payments"
    )

    def __repr__(self) -> str:
        return (
            f"<PurchaseOrderPayment id={self.id} order_id={self.order_id} "
            f"amount={self.amount} date={self.payment_date}>"
        )
