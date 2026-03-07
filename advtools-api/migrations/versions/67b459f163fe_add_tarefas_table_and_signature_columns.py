"""Add tarefas table and signature columns

Revision ID: 67b459f163fe
Revises: 0ffc78776994
Create Date: 2026-03-06 17:01:08.159857

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '67b459f163fe'
down_revision: Union[str, Sequence[str], None] = '0ffc78776994'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. New Tables
    op.create_table('tarefas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('escritorio_id', sa.Integer(), sa.ForeignKey('escritorios.id'), nullable=False),
        sa.Column('processo_id', sa.Integer(), sa.ForeignKey('processos.id'), nullable=True),
        sa.Column('responsavel_id', sa.Integer(), sa.ForeignKey('usuarios.id'), nullable=True),
        sa.Column('criado_por_id', sa.Integer(), sa.ForeignKey('usuarios.id'), nullable=False),
        sa.Column('titulo', sa.String(length=255), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), server_default='Pendente', nullable=True),
        sa.Column('prioridade', sa.String(length=50), server_default='Normal', nullable=True),
        sa.Column('data_vencimento', sa.DateTime(), nullable=True),
        sa.Column('data_criacao', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('data_atualizacao', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tarefas_id'), 'tarefas', ['id'], unique=False)
    op.create_index(op.f('ix_tarefas_escritorio_id'), 'tarefas', ['escritorio_id'], unique=False)
    op.create_index(op.f('ix_tarefas_processo_id'), 'tarefas', ['processo_id'], unique=False)
    op.create_index(op.f('ix_tarefas_responsavel_id'), 'tarefas', ['responsavel_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_tarefas_responsavel_id'), table_name='tarefas')
    op.drop_index(op.f('ix_tarefas_processo_id'), table_name='tarefas')
    op.drop_index(op.f('ix_tarefas_escritorio_id'), table_name='tarefas')
    op.drop_index(op.f('ix_tarefas_id'), table_name='tarefas')
    op.drop_table('tarefas')
