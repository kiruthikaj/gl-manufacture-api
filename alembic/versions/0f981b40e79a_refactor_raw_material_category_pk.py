"""refactor_raw_material_category_pk

Revision ID: 0f981b40e79a
Revises: 821e5400ab61
Create Date: 2026-05-31 06:13:50.191172

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '0f981b40e79a'
down_revision: Union[str, None] = '821e5400ab61'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Drop the old FK on raw_materials first (it references raw_material_categories.id)
    op.drop_constraint('raw_materials_category_id_fkey', 'raw_materials', type_='foreignkey')

    # 2. Migrate raw_materials.category_id from UUID → VARCHAR(20)
    op.alter_column(
        'raw_materials', 'category_id',
        existing_type=sa.UUID(),
        type_=sa.String(length=20),
        existing_nullable=True,
        postgresql_using='NULL',  # existing rows had UUID refs; safe to NULL since table is empty
    )

    # 3. Drop unique constraint on raw_category_code (PK uniqueness replaces it)
    op.drop_constraint(
        'raw_material_categories_raw_category_code_key',
        'raw_material_categories',
        type_='unique',
    )

    # 4. Drop the old PK constraint on id
    op.drop_constraint('raw_material_categories_pkey', 'raw_material_categories', type_='primary')

    # 5. Drop removed columns
    op.drop_column('raw_material_categories', 'available_date')
    op.drop_column('raw_material_categories', 'available_qty')
    op.drop_column('raw_material_categories', 'min_required_qty')
    op.drop_column('raw_material_categories', 'id')

    # 6. Resize raw_category_code VARCHAR(50) → VARCHAR(20)
    op.alter_column(
        'raw_material_categories', 'raw_category_code',
        existing_type=sa.VARCHAR(length=50),
        type_=sa.String(length=20),
        existing_nullable=False,
    )

    # 7. Promote raw_category_code to primary key
    op.create_primary_key('raw_material_categories_pkey', 'raw_material_categories', ['raw_category_code'])

    # 8. Add the new FK pointing to raw_category_code
    op.create_foreign_key(
        'raw_materials_category_id_fkey',
        'raw_materials', 'raw_material_categories',
        ['category_id'], ['raw_category_code'],
    )


def downgrade() -> None:
    op.drop_constraint('raw_materials_category_id_fkey', 'raw_materials', type_='foreignkey')
    op.alter_column(
        'raw_materials', 'category_id',
        existing_type=sa.String(length=20),
        type_=sa.UUID(),
        existing_nullable=True,
        postgresql_using='NULL',
    )
    op.drop_constraint('raw_material_categories_pkey', 'raw_material_categories', type_='primary')
    op.alter_column(
        'raw_material_categories', 'raw_category_code',
        existing_type=sa.String(length=20),
        type_=sa.VARCHAR(length=50),
        existing_nullable=False,
    )
    op.add_column('raw_material_categories', sa.Column('id', sa.UUID(), autoincrement=False, nullable=False))
    op.add_column('raw_material_categories', sa.Column('available_date', sa.DATE(), autoincrement=False, nullable=True))
    op.add_column('raw_material_categories', sa.Column('available_qty', sa.NUMERIC(precision=12, scale=3), autoincrement=False, nullable=True))
    op.add_column('raw_material_categories', sa.Column('min_required_qty', sa.NUMERIC(precision=12, scale=3), autoincrement=False, nullable=True))
    op.create_primary_key('raw_material_categories_pkey', 'raw_material_categories', ['id'])
    op.create_unique_constraint('raw_material_categories_raw_category_code_key', 'raw_material_categories', ['raw_category_code'])
    op.create_foreign_key('raw_materials_category_id_fkey', 'raw_materials', 'raw_material_categories', ['category_id'], ['id'])
