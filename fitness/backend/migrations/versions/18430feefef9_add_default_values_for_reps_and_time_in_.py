"""Add default values for reps and time in workout_plan_sets

Revision ID: 18430feefef9
Revises: 660c5e77944c
Create Date: 2025-01-23 19:36:22.767116

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '18430feefef9'
down_revision: Union[str, None] = '660c5e77944c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create a temporary table with the updated schema
    op.create_table(
        'workout_plan_sets_new',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('exercise_id', sa.Integer, sa.ForeignKey('workout_plan_exercises.id', ondelete='CASCADE')),
        sa.Column('reps', sa.Integer, nullable=True, server_default='0'),  # Default value
        sa.Column('weight', sa.Float, nullable=True),
        sa.Column('time', sa.Float, nullable=True, server_default='0.0'),  # Default value
        sa.Column('completed', sa.Boolean, nullable=True),
    )

    # Copy data from the old table to the new table
    op.execute(
        """
        INSERT INTO workout_plan_sets_new (id, exercise_id, reps, weight, time, completed)
        SELECT id, exercise_id, COALESCE(reps, 0), weight, COALESCE(time, 0.0), completed
        FROM workout_plan_sets
        """
    )

    # Drop the old table
    op.drop_table('workout_plan_sets')

    # Rename the new table to the original name
    op.rename_table('workout_plan_sets_new', 'workout_plan_sets')


def downgrade() -> None:
    # Recreate the original table without defaults
    op.create_table(
        'workout_plan_sets',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('exercise_id', sa.Integer, sa.ForeignKey('workout_plan_exercises.id', ondelete='CASCADE')),
        sa.Column('reps', sa.Integer, nullable=True),
        sa.Column('weight', sa.Float, nullable=True),
        sa.Column('time', sa.Float, nullable=True),
        sa.Column('completed', sa.Boolean, nullable=True),
    )

    # Copy data back to the original table
    op.execute(
        """
        INSERT INTO workout_plan_sets (id, exercise_id, reps, weight, time, completed)
        SELECT id, exercise_id, NULLIF(reps, 0), weight, NULLIF(time, 0.0), completed
        FROM workout_plan_sets_new
        """
    )

    # Drop the temporary table
    op.drop_table('workout_plan_sets_new')