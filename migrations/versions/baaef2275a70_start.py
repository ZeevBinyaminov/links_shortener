"""start

Revision ID: baaef2275a70
Revises: 431b6a6c29e5
Create Date: 2026-03-22 15:36:19.149285

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'baaef2275a70'
down_revision: Union[str, Sequence[str], None] = '431b6a6c29e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
