"""rename_raw_material_id_and_category_id

Rename raw_materials.id -> material_code
Rename raw_materials.category_id -> category_code

PostgreSQL's RENAME COLUMN automatically updates all FK constraints that
reference the renamed column, so no explicit FK drop/recreate is needed.

Revision ID: b2b5ebbb1085
Revises: 0f981b40e79a
Create Date: 2026-05-31 06:45:50.901469

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'b2b5ebbb1085'
down_revision: Union[str, None] = '0f981b40e79a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('raw_materials', 'id', new_column_name='material_code')
    op.alter_column('raw_materials', 'category_id', new_column_name='category_code')


def downgrade() -> None:
    op.alter_column('raw_materials', 'category_code', new_column_name='category_id')
    op.alter_column('raw_materials', 'material_code', new_column_name='id')
