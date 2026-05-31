from app.repositories.base import BaseRepository

# Supplier domain
from app.repositories.supplier import SupplierRepository

# Raw-material domain
from app.repositories.raw_material import (
    RawMaterialCategoryRepository,
    RawMaterialRepository,
)

# Inventory
from app.repositories.free_stock_item import FreeStockItemRepository

# Purchase-order domain
from app.repositories.purchase_order import (
    PurchaseOrderItemRepository,
    PurchaseOrderPaymentRepository,
    PurchaseOrderRepository,
)

# Finished-goods catalog
from app.repositories.product import ProductRepository

# Sales domain
from app.repositories.sales_rep import SalesRepRepository
from app.repositories.sales_order import SalesOrderItemRepository, SalesOrderRepository

# HR / utilities
from app.repositories.employee import EmployeeRepository
from app.repositories.holiday import HolidayRepository

__all__ = [
    "BaseRepository",
    # Supplier
    "SupplierRepository",
    # Raw materials
    "RawMaterialRepository",
    "RawMaterialCategoryRepository",
    # Inventory
    "FreeStockItemRepository",
    # Purchase orders
    "PurchaseOrderRepository",
    "PurchaseOrderItemRepository",
    "PurchaseOrderPaymentRepository",
    # Products
    "ProductRepository",
    # Sales
    "SalesRepRepository",
    "SalesOrderRepository",
    "SalesOrderItemRepository",
    # HR / utilities
    "EmployeeRepository",
    "HolidayRepository",
]
