"""fix employee table

Revision ID: 018c5b949ca3
Revises: 099c4390ca73
Create Date: 2024-11-09 11:16:17.241157

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '018c5b949ca3'
down_revision: Union[str, None] = '099c4390ca73'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('employees', 'id', existing_type=sa.Integer, autoincrement=True)
    op.alter_column('employees', 'fistname', new_column_name='firstname')

def downgrade() -> None:
    op.alter_column('employees', 'id', existing_type=sa.Integer, autoincrement=True)
    op.alter_column('employees', 'fistname', new_column_name='firstname')
