"""Consolidacao Processos

Revision ID: e7b23d90f1a2
Revises: d3c3ba90d8d8
Create Date: 2026-03-04 15:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'e7b23d90f1a2'
down_revision: Union[str, Sequence[str], None] = 'd3c3ba90d8d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Tabelas Pastas de Trabalho e Tipos de Serviço
    op.create_table('pastas_trabalho',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('escritorio_id', sa.Integer(), sa.ForeignKey('escritorios.id'), nullable=False),
        sa.Column('nome', sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pastas_trabalho_id'), 'pastas_trabalho', ['id'], unique=False)
    op.create_index(op.f('ix_pastas_trabalho_escritorio_id'), 'pastas_trabalho', ['escritorio_id'], unique=False)

    op.create_table('tipos_servico',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('escritorio_id', sa.Integer(), sa.ForeignKey('escritorios.id'), nullable=False),
        sa.Column('nome', sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tipos_servico_id'), 'tipos_servico', ['id'], unique=False)
    op.create_index(op.f('ix_tipos_servico_escritorio_id'), 'tipos_servico', ['escritorio_id'], unique=False)

    # 2. Tabela Processos
    op.create_table('processos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('escritorio_id', sa.Integer(), sa.ForeignKey('escritorios.id'), nullable=False),
        sa.Column('cliente_id', sa.Integer(), sa.ForeignKey('clientes.id'), nullable=True),
        sa.Column('advogado_responsavel_id', sa.Integer(), sa.ForeignKey('usuarios.id'), nullable=True),
        sa.Column('pasta_trabalho_id', sa.Integer(), sa.ForeignKey('pastas_trabalho.id'), nullable=True),
        sa.Column('numero_processo', sa.String(length=50), nullable=True),
        sa.Column('tribunal', sa.String(length=20), nullable=True),
        sa.Column('grau', sa.String(length=5), server_default='G1', nullable=True),
        sa.Column('data_ajuizamento', sa.DateTime(), nullable=True),
        sa.Column('nivel_sigilo', sa.Integer(), server_default='0', nullable=True),
        sa.Column('classe_codigo', sa.Integer(), nullable=True),
        sa.Column('classe_nome', sa.String(length=255), nullable=True),
        sa.Column('orgao_julgador_codigo', sa.Integer(), nullable=True),
        sa.Column('orgao_julgador_nome', sa.String(length=255), nullable=True),
        sa.Column('orgao_julgador_municipio_ibge', sa.Integer(), nullable=True),
        sa.Column('formato_codigo', sa.Integer(), nullable=True),
        sa.Column('formato_nome', sa.String(length=100), server_default='Eletrônico', nullable=True),
        sa.Column('sistema_codigo', sa.Integer(), nullable=True),
        sa.Column('sistema_nome', sa.String(length=100), nullable=True),
        sa.Column('titulo', sa.String(length=255), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), server_default='Ativo', nullable=True),
        sa.Column('prioridade', sa.String(length=50), server_default='Normal', nullable=True),
        sa.Column('valor_causa', sa.Float(), nullable=True),
        sa.Column('area_direito', sa.String(length=100), nullable=True),
        sa.Column('fase_processual', sa.String(length=100), nullable=True),
        sa.Column('polo', sa.String(length=50), server_default='Autor', nullable=True),
        sa.Column('data_criacao', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('data_atualizacao', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_processos_id'), 'processos', ['id'], unique=False)
    op.create_index(op.f('ix_processos_escritorio_id'), 'processos', ['escritorio_id'], unique=False)
    op.create_index(op.f('ix_processos_cliente_id'), 'processos', ['cliente_id'], unique=False)
    op.create_index(op.f('ix_processos_numero_processo'), 'processos', ['numero_processo'], unique=False)

    # 3. Partes, Assuntos e Movimentacoes
    op.create_table('processo_partes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('processo_id', sa.Integer(), sa.ForeignKey('processos.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tipo_parte', sa.String(length=100), nullable=False),
        sa.Column('nome', sa.String(length=255), nullable=False),
        sa.Column('cpf_cnpj', sa.String(length=50), nullable=True),
        sa.Column('tipo_pessoa', sa.String(length=50), server_default='Física', nullable=True),
        sa.Column('advogado_nome', sa.String(length=255), nullable=True),
        sa.Column('advogado_oab', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_processo_partes_id'), 'processo_partes', ['id'], unique=False)

    op.create_table('processo_assuntos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('processo_id', sa.Integer(), sa.ForeignKey('processos.id', ondelete='CASCADE'), nullable=False),
        sa.Column('codigo_tpu', sa.Integer(), nullable=True),
        sa.Column('nome', sa.String(length=255), nullable=False),
        sa.Column('principal', sa.Boolean(), server_default='false', nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_processo_assuntos_id'), 'processo_assuntos', ['id'], unique=False)

    op.create_table('movimentacoes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('processo_id', sa.Integer(), sa.ForeignKey('processos.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tipo', sa.String(length=50), nullable=False),
        sa.Column('codigo_movimento', sa.Integer(), nullable=True),
        sa.Column('nome_movimento', sa.String(length=255), nullable=False),
        sa.Column('complementos_json', sa.Text(), nullable=True),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('orgao_julgador_codigo', sa.Integer(), nullable=True),
        sa.Column('orgao_julgador_nome', sa.String(length=255), nullable=True),
        sa.Column('data_hora', sa.DateTime(), nullable=False),
        sa.Column('data_registro', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('registrado_por_id', sa.Integer(), sa.ForeignKey('usuarios.id'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_movimentacoes_id'), 'movimentacoes', ['id'], unique=False)


def downgrade() -> None:
    op.drop_table('movimentacoes')
    op.drop_table('processo_assuntos')
    op.drop_table('processo_partes')
    op.drop_table('processos')
    op.drop_table('tipos_servico')
    op.drop_table('pastas_trabalho')
