"""add_owner_id

Revision ID: 3fdce051064c
Revises: 0210a2640772
Create Date: 2026-09-27 09:56:49.611612

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3fdce051064c'
down_revision: Union[str, Sequence[str], None] = '0210a2640772'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('incidents', sa.Column('owner_id', sa.String(length=255), nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('incidents', 'owner_id')
