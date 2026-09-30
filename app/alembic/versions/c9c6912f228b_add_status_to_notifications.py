"""add status to notifications

Revision ID: c9c6912f228b
Revises: 995d8dfb1761
Create Date: 2026-09-30 13:58:50.372567

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c9c6912f228b'
down_revision: Union[str, Sequence[str], None] = '995d8dfb1761'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

delivery_status = postgresql.ENUM(
    'SCHEDULED',
    'DELIVERED',
    name='delivery_status',
    create_type=False,
)


def upgrade() -> None:
    """Upgrade schema."""
    delivery_status.create(op.get_bind(), checkfirst=True)
    op.add_column(
        'notifications',
        sa.Column(
            'status',
            delivery_status,
            server_default='SCHEDULED',
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('notifications', 'status')
    delivery_status.drop(op.get_bind(), checkfirst=True)
