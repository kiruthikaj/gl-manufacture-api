from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.supplier import PaymentTerms, SupplierStatus
from app.schemas.raw_material import RawMaterialCategoryRead


class SupplierCreate(BaseModel):
    business_name: str = Field(..., min_length=1, max_length=255)
    gst_number: str | None = Field(None, max_length=20)
    contact_person: str = Field(..., min_length=1, max_length=150)
    phone: str = Field(..., min_length=1, max_length=20)
    telephone_2: str | None = Field(None, max_length=20)
    email: EmailStr | None = None
    address: str | None = Field(None, max_length=500)
    city: str | None = Field(None, max_length=100)
    payment_terms: PaymentTerms = PaymentTerms.NET_30
    status: SupplierStatus = SupplierStatus.ACTIVE
    raw_category_codes: list[str] = Field(default_factory=list)


class SupplierUpdate(BaseModel):
    business_name: str | None = Field(None, min_length=1, max_length=255)
    gst_number: str | None = Field(None, max_length=20)
    contact_person: str | None = Field(None, min_length=1, max_length=150)
    phone: str | None = Field(None, min_length=1, max_length=20)
    telephone_2: str | None = Field(None, max_length=20)
    email: EmailStr | None = None
    address: str | None = Field(None, max_length=500)
    city: str | None = Field(None, max_length=100)
    payment_terms: PaymentTerms | None = None
    status: SupplierStatus | None = None
    raw_category_codes: list[str] | None = None


class SupplierRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    business_name: str
    gst_number: str | None
    contact_person: str
    phone: str
    telephone_2: str | None
    email: str | None
    address: str | None
    city: str | None
    payment_terms: PaymentTerms
    status: SupplierStatus
    created_at: datetime
    updated_at: datetime


class SupplierDetail(SupplierRead):
    raw_material_categories: list[RawMaterialCategoryRead] = []
