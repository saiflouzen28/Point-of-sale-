"""fix employee table

Revision ID: 5b0c7b00274f
Revises: 018c5b949ca3
Create Date: 2024-11-09 11:23:24.582106

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b0c7b00274f'
down_revision: Union[str, None] = '018c5b949ca3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('employees', 'id', existing_type=sa.Integer, autoincrement=True)
    op.alter_column('employees', 'fistname', new_column_name='firstname')

def downgrade() -> None:
    op.alter_column('employees', 'id', existing_type=sa.Integer, autoincrement=True)
    op.alter_column('employees', 'fistname', new_column_name='firstname')
