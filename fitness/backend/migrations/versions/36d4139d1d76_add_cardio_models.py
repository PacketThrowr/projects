"""add_cardio_models

Revision ID: 36d4139d1d76
Revises: c847ef06e130
Create Date: 2025-01-22 16:02:47.786565

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '36d4139d1d76'
down_revision: Union[str, None] = 'c847ef06e130'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Delete existing cardio_sessions table to recreate it with correct relationship
    op.drop_table('cardio_gps_data')
    op.drop_table('cardio_health_data')
    op.drop_table('cardio_sessions')
    
    op.create_table('cardio_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('profile_id', sa.Integer(), nullable=False),
        sa.Column('exercise_id', sa.Integer(), nullable=False),
        sa.Column('duration', sa.Float(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['exercise_id'], ['exercises.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('cardio_health_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('heart_rate', sa.Integer(), nullable=True),
        sa.Column('calories', sa.Float(), nullable=True),
        sa.Column('steps', sa.Integer(), nullable=True),
        sa.Column('distance', sa.Float(), nullable=True),
        sa.Column('timestamp', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['cardio_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('cardio_gps_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('elevation', sa.Float(), nullable=True),
        sa.Column('timestamp', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['cardio_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('cardio_gps_data')
    op.drop_table('cardio_health_data')
    op.drop_table('cardio_sessions')
