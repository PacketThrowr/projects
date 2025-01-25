"""add recorded_type to exercises table

Revision ID: bba75cb4cb40
Revises: 33917792ca81
Create Date: 2025-01-25 02:16:14.816343

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bba75cb4cb40'
down_revision: Union[str, None] = '33917792ca81'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the existing exercises table
    op.drop_table("exercises")

    # Recreate the exercises table with the updated schema
    op.create_table(
        "exercises",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("name", sa.String, unique=True, nullable=False),
        sa.Column("force", sa.String, nullable=True),
        sa.Column("level", sa.String, nullable=True),
        sa.Column("mechanic", sa.String, nullable=True),
        sa.Column("equipment", sa.String, nullable=True),
        sa.Column("primaryMuscles", sa.JSON, nullable=True),
        sa.Column("secondaryMuscles", sa.JSON, nullable=True),
        sa.Column("instructions", sa.JSON, nullable=True),
        sa.Column("category", sa.String, nullable=True),
        sa.Column("picture", sa.String, nullable=True),
        sa.Column("recorded_type", sa.String, nullable=True),
    )


def downgrade() -> None:
    # Revert to the old structure of the exercises table
    op.drop_table("exercises")
    op.create_table(
        "exercises",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("name", sa.String, unique=True, nullable=False),
        sa.Column("picture", sa.String, nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("type", sa.String, nullable=False),
        sa.Column("weight_type", sa.String, nullable=True),
        sa.Column("muscle_category", sa.String, nullable=True),
        sa.Column("muscle_groups", sa.JSON, nullable=True),
        sa.Column("measurement_type", sa.String, nullable=False),
    )