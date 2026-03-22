"""start

Revision ID: 431b6a6c29e5
Revises: b2bd912f9e8c
Create Date: 2026-03-22 15:30:06.241416

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '431b6a6c29e5'
down_revision: Union[str, Sequence[str], None] = 'b2bd912f9e8c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
