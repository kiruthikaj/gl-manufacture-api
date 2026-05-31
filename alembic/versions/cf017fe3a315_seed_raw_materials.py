"""seed_raw_materials

Revision ID: cf017fe3a315
Revises: b2b5ebbb1085
Create Date: 2026-05-31 06:54:08.550128

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text

revision: str = 'cf017fe3a315'
down_revision: Union[str, None] = 'b2b5ebbb1085'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


RECORDS = [
    # ── Mix ──────────────────────────────────────────────────────────
    ("MIX-MLKPWD",    "MIX",  "Milk Powder",           "KG"),
    ("MIX-WATER",     "MIX",  "Water",                 "LITRE"),
    ("MIX-VNSPTH",    "MIX",  "Vanaspathi",            "KG"),
    ("MIX-SUGAR",     "MIX",  "Sugar",                 "KG"),

    # ── Essence ──────────────────────────────────────────────────────
    ("ESS-VANILLA",   "ESS",  "Vanilla Essence",       "ML"),
    ("ESS-MILK",      "ESS",  "Milk Essence",          "ML"),
    ("ESS-STRBRY",    "ESS",  "Strawberry Essence",    "ML"),
    ("ESS-BTRSCTH",   "ESS",  "Butterscotch Essence",  "ML"),
    ("ESS-PISTA",     "ESS",  "Pista Essence",         "ML"),

    # ── Cup ──────────────────────────────────────────────────────────
    ("CUP-50ML",      "CUP",  "50ml Cup",              "PIECE"),
    ("CUP-100ML",     "CUP",  "100ml Cup",             "PIECE"),

    # ── Lid (cups + cones) ───────────────────────────────────────────
    ("LID-50ML",      "LID",  "50ml Lid",              "PIECE"),
    ("LID-100ML",     "LID",  "100ml Lid",             "PIECE"),
    ("LID-CONE-SM",   "LID",  "Small Cone Lid",        "PIECE"),
    ("LID-CONE-BG",   "LID",  "Big Cone Lid",          "PIECE"),

    # ── Cone ─────────────────────────────────────────────────────────
    ("CNE-SM-VAN",    "CNE",  "Small Vanilla Cone",    "PIECE"),
    ("CNE-SM-STR",    "CNE",  "Small Strawberry Cone", "PIECE"),
    ("CNE-SM-CHO",    "CNE",  "Small Chocolate Cone",  "PIECE"),
    ("CNE-SM-BUT",    "CNE",  "Small Butter Cone",     "PIECE"),
    ("CNE-BG-VAN",    "CNE",  "Big Vanilla Cone",      "PIECE"),
    ("CNE-BG-STR",    "CNE",  "Big Strawberry Cone",   "PIECE"),
    ("CNE-BG-CHO",    "CNE",  "Big Chocolate Cone",    "PIECE"),
    ("CNE-BG-BUT",    "CNE",  "Big Butter Cone",       "PIECE"),

    # ── Ball ─────────────────────────────────────────────────────────
    ("BALL-STRBRY",   "BALL", "Strawberry Ball",       "PIECE"),
    ("BALL-MANGO",    "BALL", "Mango Ball",            "PIECE"),
    ("BALL-POT",      "BALL", "Pot",                   "PIECE"),
    ("BALL-SNDGLS",   "BALL", "Sunday Glass",          "PIECE"),
]


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text("""
            INSERT INTO raw_materials
                (material_code, category_code, material_name, unit, available_quantity)
            VALUES
                (:material_code, :category_code, :material_name,
                 CAST(:unit AS materialunit), 0)
            ON CONFLICT (material_name) DO NOTHING
        """),
        [
            {"material_code": mc, "category_code": cat,
             "material_name": name, "unit": unit}
            for mc, cat, name, unit in RECORDS
        ],
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text("DELETE FROM raw_materials WHERE material_code = ANY(:codes)"),
        {"codes": [mc for mc, _, _, _ in RECORDS]},
    )
