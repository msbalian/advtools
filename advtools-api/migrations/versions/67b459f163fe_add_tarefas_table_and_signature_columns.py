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
    op.create_table('signatarios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('documento_id', sa.Integer(), sa.ForeignKey('documentos_cliente.id'), nullable=False),
        sa.Column('token_acesso', sa.String(length=32), nullable=False),
        sa.Column('nome', sa.String(length=200), nullable=False),
        sa.Column('email', sa.String(length=150), nullable=False),
        sa.Column('cpf', sa.String(length=20), nullable=True),
        sa.Column('funcao', sa.String(length=100), server_default='Parte', nullable=True),
        sa.Column('status', sa.String(length=50), server_default='Pendente', nullable=True),
        sa.Column('data_visualizacao', sa.DateTime(), nullable=True),
        sa.Column('data_assinatura', sa.DateTime(), nullable=True),
        sa.Column('ip_assinatura', sa.String(length=50), nullable=True),
        sa.Column('user_agent_assinatura', sa.String(length=500), nullable=True),
        sa.Column('tipo_autenticacao', sa.String(length=50), nullable=True),
        sa.Column('imagem_assinatura_path', sa.String(length=300), nullable=True),
        sa.Column('page_number', sa.Integer(), nullable=True),
        sa.Column('x_pos', sa.Float(), nullable=True),
        sa.Column('y_pos', sa.Float(), nullable=True),
        sa.Column('width', sa.Float(), nullable=True),
        sa.Column('height', sa.Float(), nullable=True),
        sa.Column('docwidth', sa.Float(), nullable=True),
        sa.Column('docheight', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_signatarios_id'), 'signatarios', ['id'], unique=False)
    op.create_index(op.f('ix_signatarios_token_acesso'), 'signatarios', ['token_acesso'], unique=True)
    op.create_index(op.f('ix_signatarios_documento_id'), 'signatarios', ['documento_id'], unique=False)

    op.create_table('signatarios_posicoes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('signatario_id', sa.Integer(), sa.ForeignKey('signatarios.id', ondelete='CASCADE'), nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=False),
        sa.Column('x_pos', sa.Float(), nullable=False),
        sa.Column('y_pos', sa.Float(), nullable=False),
        sa.Column('width', sa.Float(), nullable=False),
        sa.Column('height', sa.Float(), nullable=False),
        sa.Column('docwidth', sa.Float(), nullable=False),
        sa.Column('docheight', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_signatarios_posicoes_id'), 'signatarios_posicoes', ['id'], unique=False)
    op.create_index(op.f('ix_signatarios_posicoes_signatario_id'), 'signatarios_posicoes', ['signatario_id'], unique=False)

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

    # 2. Add columns to documentos_cliente
    op.add_column('documentos_cliente', sa.Column('token_assinatura', sa.String(length=32), nullable=True))
    op.add_column('documentos_cliente', sa.Column('status_assinatura', sa.String(length=50), server_default='Aguardando', nullable=True))
    op.add_column('documentos_cliente', sa.Column('arquivo_assinado_path', sa.String(length=500), nullable=True))
    op.add_column('documentos_cliente', sa.Column('hash_original', sa.String(length=64), nullable=True))
    op.add_column('documentos_cliente', sa.Column('hash_assinado', sa.String(length=64), nullable=True))
    op.add_column('documentos_cliente', sa.Column('token_validacao', sa.String(length=32), nullable=True))
    
    op.create_index(op.f('ix_documentos_cliente_token_assinatura'), 'documentos_cliente', ['token_assinatura'], unique=True)
    op.create_index(op.f('ix_documentos_cliente_token_validacao'), 'documentos_cliente', ['token_validacao'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_documentos_cliente_token_validacao'), table_name='documentos_cliente')
    op.drop_index(op.f('ix_documentos_cliente_token_assinatura'), table_name='documentos_cliente')
    op.drop_column('documentos_cliente', 'token_validacao')
    op.drop_column('documentos_cliente', 'hash_assinado')
    op.drop_column('documentos_cliente', 'hash_original')
    op.drop_column('documentos_cliente', 'arquivo_assinado_path')
    op.drop_column('documentos_cliente', 'status_assinatura')
    op.drop_column('documentos_cliente', 'token_assinatura')

    op.drop_index(op.f('ix_tarefas_responsavel_id'), table_name='tarefas')
    op.drop_index(op.f('ix_tarefas_processo_id'), table_name='tarefas')
    op.drop_index(op.f('ix_tarefas_escritorio_id'), table_name='tarefas')
    op.drop_index(op.f('ix_tarefas_id'), table_name='tarefas')
    op.drop_table('tarefas')

    op.drop_index(op.f('ix_signatarios_posicoes_signatario_id'), table_name='signatarios_posicoes')
    op.drop_index(op.f('ix_signatarios_posicoes_id'), table_name='signatarios_posicoes')
    op.drop_table('signatarios_posicoes')

    op.drop_index(op.f('ix_signatarios_documento_id'), table_name='signatarios')
    op.drop_index(op.f('ix_signatarios_token_acesso'), table_name='signatarios')
    op.drop_index(op.f('ix_signatarios_id'), table_name='signatarios')
    op.drop_table('signatarios')
