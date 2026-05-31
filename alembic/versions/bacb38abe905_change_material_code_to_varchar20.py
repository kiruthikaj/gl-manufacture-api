"""change_material_code_to_varchar20

Changes raw_materials.material_code from UUID → VARCHAR(20).
Dependent FK columns in free_stock_items and purchase_order_items follow suit.
Existing seed data (UUID-style codes) is replaced with the short string codes.

Revision ID: bacb38abe905
Revises: cf017fe3a315
Create Date: 2026-05-31 07:51:08.714503

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text

revision: str = 'bacb38abe905'
down_revision: Union[str, None] = 'cf017fe3a315'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Short-code seed data that replaces the UUID-keyed rows from cf017fe3a315
RECORDS = [
    ("MIX-MLKPWD",    "MIX",  "Milk Powder",           "KG"),
    ("MIX-WATER",     "MIX",  "Water",                 "LITRE"),
    ("MIX-VNSPTH",    "MIX",  "Vanaspathi",            "KG"),
    ("MIX-SUGAR",     "MIX",  "Sugar",                 "KG"),
    ("ESS-VANILLA",   "ESS",  "Vanilla Essence",       "ML"),
    ("ESS-MILK",      "ESS",  "Milk Essence",          "ML"),
    ("ESS-STRBRY",    "ESS",  "Strawberry Essence",    "ML"),
    ("ESS-BTRSCTH",   "ESS",  "Butterscotch Essence",  "ML"),
    ("ESS-PISTA",     "ESS",  "Pista Essence",         "ML"),
    ("CUP-50ML",      "CUP",  "50ml Cup",              "PIECE"),
    ("CUP-100ML",     "CUP",  "100ml Cup",             "PIECE"),
    ("LID-50ML",      "LID",  "50ml Lid",              "PIECE"),
    ("LID-100ML",     "LID",  "100ml Lid",             "PIECE"),
    ("LID-CONE-SM",   "LID",  "Small Cone Lid",        "PIECE"),
    ("LID-CONE-BG",   "LID",  "Big Cone Lid",          "PIECE"),
    ("CNE-SM-VAN",    "CNE",  "Small Vanilla Cone",    "PIECE"),
    ("CNE-SM-STR",    "CNE",  "Small Strawberry Cone", "PIECE"),
    ("CNE-SM-CHO",    "CNE",  "Small Chocolate Cone",  "PIECE"),
    ("CNE-SM-BUT",    "CNE",  "Small Butter Cone",     "PIECE"),
    ("CNE-BG-VAN",    "CNE",  "Big Vanilla Cone",      "PIECE"),
    ("CNE-BG-STR",    "CNE",  "Big Strawberry Cone",   "PIECE"),
    ("CNE-BG-CHO",    "CNE",  "Big Chocolate Cone",    "PIECE"),
    ("CNE-BG-BUT",    "CNE",  "Big Butter Cone",       "PIECE"),
    ("BALL-STRBRY",   "BALL", "Strawberry Ball",       "PIECE"),
    ("BALL-MANGO",    "BALL", "Mango Ball",            "PIECE"),
    ("BALL-POT",      "BALL", "Pot",                   "PIECE"),
    ("BALL-SNDGLS",   "BALL", "Sunday Glass",          "PIECE"),
]


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Drop FKs that reference raw_materials.material_code
    op.drop_constraint('free_stock_items_material_id_fkey', 'free_stock_items', type_='foreignkey')
    op.drop_constraint('purchase_order_items_material_id_fkey', 'purchase_order_items', type_='foreignkey')

    # 2. Remove UUID-keyed seed rows (they were 36 chars, won't fit in VARCHAR(20))
    conn.execute(text("DELETE FROM raw_materials"))

    # 3. Change column types: UUID → VARCHAR(20)
    op.alter_column(
        'raw_materials', 'material_code',
        existing_type=sa.UUID(),
        type_=sa.String(20),
        existing_nullable=False,
        postgresql_using='material_code::text',
    )
    op.alter_column(
        'free_stock_items', 'material_id',
        existing_type=sa.UUID(),
        type_=sa.String(20),
        existing_nullable=False,
        postgresql_using='material_id::text',
    )
    op.alter_column(
        'purchase_order_items', 'material_id',
        existing_type=sa.UUID(),
        type_=sa.String(20),
        existing_nullable=False,
        postgresql_using='material_id::text',
    )

    # 4. Re-insert seed data with short string codes
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

    # 5. Recreate FKs against the new VARCHAR(20) PK
    op.create_foreign_key(
        'free_stock_items_material_id_fkey',
        'free_stock_items', 'raw_materials',
        ['material_id'], ['material_code'],
    )
    op.create_foreign_key(
        'purchase_order_items_material_id_fkey',
        'purchase_order_items', 'raw_materials',
        ['material_id'], ['material_code'],
    )


def downgrade() -> None:
    conn = op.get_bind()

    op.drop_constraint('free_stock_items_material_id_fkey', 'free_stock_items', type_='foreignkey')
    op.drop_constraint('purchase_order_items_material_id_fkey', 'purchase_order_items', type_='foreignkey')

    conn.execute(text("DELETE FROM raw_materials"))

    op.alter_column(
        'raw_materials', 'material_code',
        existing_type=sa.String(20),
        type_=sa.UUID(),
        existing_nullable=False,
        postgresql_using='material_code::uuid',
    )
    op.alter_column(
        'free_stock_items', 'material_id',
        existing_type=sa.String(20),
        type_=sa.UUID(),
        existing_nullable=False,
        postgresql_using='material_id::uuid',
    )
    op.alter_column(
        'purchase_order_items', 'material_id',
        existing_type=sa.String(20),
        type_=sa.UUID(),
        existing_nullable=False,
        postgresql_using='material_id::uuid',
    )

    op.create_foreign_key(
        'free_stock_items_material_id_fkey',
        'free_stock_items', 'raw_materials',
        ['material_id'], ['material_code'],
    )
    op.create_foreign_key(
        'purchase_order_items_material_id_fkey',
        'purchase_order_items', 'raw_materials',
        ['material_id'], ['material_code'],
    )
