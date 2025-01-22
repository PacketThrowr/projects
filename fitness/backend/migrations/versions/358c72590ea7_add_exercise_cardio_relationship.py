"""add_exercise_cardio_relationship

Revision ID: 358c72590ea7
Revises: 3e5a3c87b460
Create Date: 2025-01-22 16:08:39.223395

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '358c72590ea7'
down_revision: Union[str, None] = '3e5a3c87b460'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
