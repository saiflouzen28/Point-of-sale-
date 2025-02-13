"""Add address column to employees table

Revision ID: 099c4390ca73
Revises: 32f33976a296
Create Date: 2024-11-05 17:11:26.926502

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '099c4390ca73'
down_revision: Union[str, None] = '32f33976a296'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('employees', sa.Column('created_on', sa.DateTime(), nullable=False))


def downgrade() -> None:
    op.drop_column('employees', 'created_on')