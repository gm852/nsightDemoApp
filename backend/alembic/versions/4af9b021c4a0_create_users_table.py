"""Create users table

Revision ID: 4af9b021c4a0
Revises: 
Create Date: 2025-10-02 23:47:13.916489

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4af9b021c4a0'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('website', sa.String(), nullable=False),
        sa.Column('company_name', sa.String(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username')
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop users table
    op.drop_table('users')
