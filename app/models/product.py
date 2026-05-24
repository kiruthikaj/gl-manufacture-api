import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Product(Base):
    """Finished-goods catalog — items that can appear on a sales order."""

    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # Human-readable business key (e.g. "PRD-0042")
    product_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    product_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    # Date from which minimum stock level must be maintained
    min_stock_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    min_required_qty: Mapped[Decimal | None] = mapped_column(Numeric(12, 3), nullable=True)

    # Relationships
    sales_order_items: Mapped[list["SalesOrderItem"]] = relationship(
        "SalesOrderItem", back_populates="product"
    )

    def __repr__(self) -> str:
        return f"<Product id={self.id} code={self.product_code!r} name={self.product_name!r}>"
