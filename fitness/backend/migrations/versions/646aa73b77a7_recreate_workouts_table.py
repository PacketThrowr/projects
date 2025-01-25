"""Recreate workouts table

Revision ID: 646aa73b77a7
Revises: bba75cb4cb40
Create Date: 2025-01-25 16:03:06.498294

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '646aa73b77a7'
down_revision: Union[str, None] = 'bba75cb4cb40'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the existing workouts table
    op.drop_table('workouts')

    # Recreate the workouts table with the updated schema
    op.create_table(
        'workouts',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('description', sa.String, nullable=True),
        sa.Column('profile_id', sa.Integer, sa.ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('date', sa.String, nullable=False),
        sa.Column('start_time', sa.String, nullable=True),  # New field
        sa.Column('end_time', sa.String, nullable=True),    # New field
    )


def downgrade() -> None:
    # Drop the workouts table
    op.drop_table('workouts')

    # Recreate the original workouts table without the new fields
    op.create_table(
        'workouts',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('description', sa.String, nullable=True),
        sa.Column('profile_id', sa.Integer, sa.ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('date', sa.String, nullable=False),
    )