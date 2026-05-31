from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.purchase_order import PaymentMode


# ─────────────────────────── Purchase Order Item ────────────────────────────

class PurchaseOrderItemCreate(BaseModel):
    material_id: str = Field(..., max_length=20)
    quantity: Decimal | None = Field(None, gt=0)
    unit_price: Decimal | None = Field(None, ge=0)
    rate: Decimal | None = Field(None, ge=0)


class PurchaseOrderItemUpdate(BaseModel):
    material_id: str | None = Field(None, max_length=20)
    quantity: Decimal | None = Field(None, gt=0)
    unit_price: Decimal | None = Field(None, ge=0)
    rate: Decimal | None = Field(None, ge=0)


class PurchaseOrderItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    order_id: uuid.UUID
    material_id: str
    quantity: Decimal | None
    unit_price: Decimal | None
    rate: Decimal | None


# ─────────────────────────── Purchase Order Payment ─────────────────────────

class PurchaseOrderPaymentCreate(BaseModel):
    payment_date: date
    amount: Decimal | None = Field(None, ge=0)
    mode_of_payment: PaymentMode | None = None
    payment_name: str | None = Field(None, max_length=255)


class PurchaseOrderPaymentUpdate(BaseModel):
    payment_date: date | None = None
    amount: Decimal | None = Field(None, ge=0)
    mode_of_payment: PaymentMode | None = None
    payment_name: str | None = Field(None, max_length=255)


class PurchaseOrderPaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    order_id: uuid.UUID
    payment_date: date
    amount: Decimal | None
    mode_of_payment: PaymentMode | None
    payment_name: str | None


# ─────────────────────────── Purchase Order ─────────────────────────────────

class PurchaseOrderCreate(BaseModel):
    supplier_id: uuid.UUID
    order_date: date | None = None
    due_date: date | None = None
    expected_delivery_date: date | None = None
    received_date: date | None = None
    items: list[PurchaseOrderItemCreate] = Field(default_factory=list)


class PurchaseOrderUpdate(BaseModel):
    supplier_id: uuid.UUID | None = None
    order_date: date | None = None
    due_date: date | None = None
    expected_delivery_date: date | None = None
    received_date: date | None = None


class PurchaseOrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    supplier_id: uuid.UUID
    order_date: date | None
    due_date: date | None
    expected_delivery_date: date | None
    received_date: date | None


class PurchaseOrderDetail(PurchaseOrderRead):
    items: list[PurchaseOrderItemRead] = []
    payments: list[PurchaseOrderPaymentRead] = []


class MarkReceivedRequest(BaseModel):
    received_date: date | None = None
