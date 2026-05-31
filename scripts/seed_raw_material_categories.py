"""
Seed script — inserts raw material categories.

Run from the backend root:
    python scripts/seed_raw_material_categories.py
"""

import sys
import os

# Allow imports from the project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import Database
from app.models.raw_material import RawMaterialCategory

CATEGORIES = [
    {"raw_category_code": "MIX",  "category_name": "Mix",           "primary_descriptor": "Ice cream mix bases and blends"},
    {"raw_category_code": "MISC", "category_name": "Miscellaneous",  "primary_descriptor": "General purpose and uncategorised materials"},
    {"raw_category_code": "ESS",  "category_name": "Essence",        "primary_descriptor": "Flavour essences and concentrates"},
    {"raw_category_code": "CUP",  "category_name": "Cup",            "primary_descriptor": "Serving cups and containers"},
    {"raw_category_code": "LID",  "category_name": "Lid",            "primary_descriptor": "Lids and sealing covers for cups"},
    {"raw_category_code": "CVR",  "category_name": "Cover",          "primary_descriptor": "Protective covers and wrapping materials"},
    {"raw_category_code": "CNE",  "category_name": "Cone",           "primary_descriptor": "Wafer and sugar cones"},
    {"raw_category_code": "STK",  "category_name": "Stick",          "primary_descriptor": "Ice cream sticks and handles"},
    {"raw_category_code": "BALL", "category_name": "Ball",           "primary_descriptor": "Ball-shaped mould materials"},
]


def seed() -> None:
    db = Database.get_instance().get_session()
    try:
        inserted = 0
        skipped = 0
        for data in CATEGORIES:
            existing = db.get(RawMaterialCategory, data["raw_category_code"])
            if existing:
                print(f"  SKIP  {data['raw_category_code']!r:6s}  — already exists")
                skipped += 1
            else:
                db.add(RawMaterialCategory(**data))
                print(f"  ADD   {data['raw_category_code']!r:6s}  {data['category_name']}")
                inserted += 1
        db.commit()
        print(f"\nDone — {inserted} inserted, {skipped} skipped.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
