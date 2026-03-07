"""add cliente_id to tarefas

Revision ID: b9198114d446
Revises: 15005a47dde5
Create Date: 2026-03-06 23:53:40.287558

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b9198114d446'
down_revision: Union[str, Sequence[str], None] = '15005a47dde5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('tarefas', sa.Column('cliente_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_tarefas_cliente_id'), 'tarefas', ['cliente_id'], unique=False)
    op.create_foreign_key(None, 'tarefas', 'clientes', ['cliente_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, 'tarefas', type_='foreignkey')
    op.drop_index(op.f('ix_tarefas_cliente_id'), table_name='tarefas')
    op.drop_column('tarefas', 'cliente_id')
