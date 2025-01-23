"""Add workout_plan_exercises relationships

Revision ID: 660c5e77944c
Revises: 4a2fe0bc7e63
Create Date: 2025-01-23 03:46:46.081306

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '660c5e77944c'
down_revision: Union[str, None] = '4a2fe0bc7e63'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create workout_plans table
    op.create_table(
        "workout_plans",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("description", sa.String, nullable=True),
        sa.Column("profile_id", sa.Integer, sa.ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False),
    )

    # Create workout_plan_exercises table
    op.create_table(
        "workout_plan_exercises",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("workout_plan_id", sa.Integer, sa.ForeignKey("workout_plans.id", ondelete="CASCADE")),
        sa.Column("exercise_id", sa.Integer, sa.ForeignKey("exercises.id", ondelete="CASCADE")),
    )

    # Create indexes
    op.create_index("ix_workout_plans_id", "workout_plans", ["id"])
    op.create_index("ix_workout_plan_exercises_id", "workout_plan_exercises", ["id"])



def downgrade() -> None:
    # Drop indexes and tables in reverse order
    op.drop_index("ix_workout_plan_exercises_id", table_name="workout_plan_exercises")
    op.drop_table("workout_plan_exercises")

    op.drop_index("ix_workout_plans_id", table_name="workout_plans")
    op.drop_table("workout_plans")
