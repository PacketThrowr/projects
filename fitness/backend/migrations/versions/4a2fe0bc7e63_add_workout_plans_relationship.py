"""Add workout_plans relationship

Revision ID: 4a2fe0bc7e63
Revises: ea9db7f58806
Create Date: 2025-01-23 03:40:12.501661

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4a2fe0bc7e63'
down_revision: Union[str, None] = 'ea9db7f58806'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("profiles", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("workout_plans", sa.Integer, nullable=True)
        )
        batch_op.create_foreign_key(
            "fk_profiles_workout_plans",  # Explicit name for the constraint
            "workout_plans",  # Referenced table
            ["workout_plans"],  # Local column(s)
            ["id"],  # Referenced column(s)
            ondelete="CASCADE",  # Optional, specify cascade behavior
        )


def downgrade() -> None:
    with op.batch_alter_table("profiles", schema=None) as batch_op:
        batch_op.drop_constraint("fk_profiles_workout_plans", type_="foreignkey")
        batch_op.drop_column("workout_plans")

