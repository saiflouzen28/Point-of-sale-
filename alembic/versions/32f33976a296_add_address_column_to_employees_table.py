"""Add address column to employees table

Revision ID: 32f33976a296
Revises: 12c34f4d1dfb
Create Date: 2024-11-05 16:57:46.531509

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '32f33976a296'
down_revision: Union[str, None] = '12c34f4d1dfb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('employees', sa.Column('address', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('employees', 'address')
