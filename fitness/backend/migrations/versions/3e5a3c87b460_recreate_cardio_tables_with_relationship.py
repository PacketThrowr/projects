"""recreate_cardio_tables_with_relationship

Revision ID: 3e5a3c87b460
Revises: 36d4139d1d76
Create Date: 2025-01-22 16:05:19.755172

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e5a3c87b460'
down_revision: Union[str, None] = '36d4139d1d76'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
