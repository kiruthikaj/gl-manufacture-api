from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class RawMaterialCategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    raw_category_code: str
    category_name: str
    primary_descriptor: str | None
