"""add tamanho column to documentos and modelos

Revision ID: 15005a47dde5
Revises: 67b459f163fe
Create Date: 2026-03-06 23:29:11.129513

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '15005a47dde5'
down_revision: Union[str, Sequence[str], None] = '67b459f163fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('documentos_cliente', sa.Column('tamanho', sa.Integer(), nullable=True))
    op.add_column('modelos_documento', sa.Column('tamanho', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('modelos_documento', 'tamanho')
    op.drop_column('documentos_cliente', 'tamanho')
