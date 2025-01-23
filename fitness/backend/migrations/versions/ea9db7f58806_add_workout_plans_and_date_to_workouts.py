"""add workout plans and date to workouts

Revision ID: ea9db7f58806
Revises: f89b66037c7c
Create Date: 2025-01-23 03:19:19.072151

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ea9db7f58806'
down_revision: Union[str, None] = 'f89b66037c7c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Recreate workouts table with date
    with op.batch_alter_table('workouts') as batch_op:
        batch_op.add_column(sa.Column('date', sa.String(), server_default='2024-01-01', nullable=False))

def downgrade() -> None:
    with op.batch_alter_table('workouts') as batch_op:
        batch_op.drop_column('date')
