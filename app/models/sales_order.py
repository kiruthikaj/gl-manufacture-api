import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class SalesOrder(Base):
    """Header record for a customer sales order."""

    __tablename__ = "sales_orders"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    sales_rep_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("sales_reps.id"), nullable=False
    )
    order_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    order_amt: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Relationships
    sales_rep: Mapped["SalesRep"] = relationship(
        "SalesRep", back_populates="sales_orders"
    )
    items: Mapped[list["SalesOrderItem"]] = relationship(
        "SalesOrderItem",
        back_populates="sales_order",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<SalesOrder id={self.id} rep_id={self.sales_rep_id} "
            f"date={self.order_date} amt={self.order_amt}>"
        )


class SalesOrderItem(Base):
    """Individual product line items within a sales order."""

    __tablename__ = "sales_order_items"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("sales_orders.id"), nullable=False
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("products.id"), nullable=False
    )
    quantity: Mapped[Decimal | None] = mapped_column(Numeric(12, 3), nullable=True)

    # Relationships
    sales_order: Mapped["SalesOrder"] = relationship(
        "SalesOrder", back_populates="items"
    )
    product: Mapped["Product"] = relationship(
        "Product", back_populates="sales_order_items"
    )

    def __repr__(self) -> str:
        return (
            f"<SalesOrderItem id={self.id} order_id={self.order_id} "
            f"product_id={self.product_id} qty={self.quantity}>"
        )
