"""url_id added to stats

Revision ID: 674ee742690e
Revises: baaef2275a70
Create Date: 2026-03-22 18:10:21.326492

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '674ee742690e'
down_revision: Union[str, Sequence[str], None] = 'baaef2275a70'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
