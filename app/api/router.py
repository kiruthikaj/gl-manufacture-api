from fastapi import APIRouter
from app.api import health, purchase_order, raw_material, supplier

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(supplier.router)
api_router.include_router(raw_material.router)
api_router.include_router(purchase_order.router)
