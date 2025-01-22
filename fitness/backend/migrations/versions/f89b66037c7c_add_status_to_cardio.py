"""add_status_to_cardio

Revision ID: f89b66037c7c
Revises: 358c72590ea7
Create Date: 2025-01-22 16:21:50.267481

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f89b66037c7c'
down_revision: Union[str, None] = '358c72590ea7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
   op.add_column('cardio_sessions', sa.Column('status', sa.String(), nullable=False, server_default='pending'))



def downgrade() -> None:
   op.drop_column('cardio_sessions', 'status')

