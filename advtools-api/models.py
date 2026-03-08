import os
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from database import Base

class Escritorio(Base):
    __tablename__ = "escritorios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    documento = Column(String(50))
    logo_path = Column(String(255))
    gemini_api_key = Column(String(255), nullable=True)
    data_criacao = Column(DateTime, default=func.now())

    usuarios = relationship("Usuario", back_populates="escritorio")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    escritorio_id = Column(Integer, ForeignKey("escritorios.id"), nullable=False)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    tipo = Column(String(50), default="Humano")
    perfil = Column(String(50), default="Colaborador")
    ativo = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    cpf = Column(String(20))
    data_criacao = Column(DateTime, default=func.now())

    escritorio = relationship("Escritorio", back_populates="usuarios")

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    escritorio_id = Column(Integer, ForeignKey("escritorios.id"), nullable=False)
    nome = Column(String(255), nullable=False)
    documento = Column(String(50)) # CPF/CNPJ
    telefone = Column(String(50))
    email = Column(String(255))
    endereco = Column(Text)
    cep = Column(String(20))
    data_nascimento = Column(String(20))
    nacionalidade = Column(String(100))
    estado_civil = Column(String(50))
    profissao = Column(String(100))
    rg = Column(String(50))
    bairro = Column(String(100))
    cidade = Column(String(100))
    uf = Column(String(2))
    data_cadastro = Column(DateTime, default=func.now())

    escritorio = relationship("Escritorio")
    servicos = relationship("Servico", back_populates="cliente")
    partes_envolvidas = relationship("ParteEnvolvida", back_populates="cliente", cascade="all, delete-orphan")
    documentos = relationship("DocumentoCliente", back_populates="cliente", cascade="all, delete-orphan")

class ParteEnvolvida(Base):
    __tablename__ = "partes_envolvidas"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    escritorio_id = Column(Integer, ForeignKey("escritorios.id"), nullable=False)
    nome = Column(String(255), nullable=False)
    documento = Column(String(50)) # CPF/CNPJ
    papel = Column(String(100)) # Papel/Função
    email = Column(String(255))
    telefone = Column(String(50))
    rg = Column(String(50))
    data_nascimento = Column(String(20))
    nacionalidade = Column(String(100))
    estado_civil = Column(String(50))
    profissao = Column(String(100))
    cep = Column(String(20))
    endereco = Column(Text)
    bairro = Column(String(100))
    cidade = Column(String(100))
    uf = Column(String(2))
    data_cadastro = Column(DateTime, default=func.now())

    cliente = relationship("Cliente", back_populates="partes_envolvidas")
    escritorio = relationship("Escritorio")


class PastaTrabalho(Base):
    __tablename__ = "pastas_trabalho"
    id = Column(Integer, primary_key=True, index=True)
    escritorio_id = Column(Integer, ForeignKey("escritorios.id"), nullable=False, index=True)
    nome = Column(String(255), nullable=False)
    escritorio = relationship("Escritorio")

class TipoServico(Base):
    __tablename__ = "tipos_servico"
    id = Column(Integer, primary_key=True, index=True)
    escritorio_id = Column(Integer, ForeignKey("escritorios.id"), nullable=False, index=True)
    nome = Column(String(255), nullable=False)
    escritorio = relationship("Escritorio")

class Servico(Base):
    __tablename__ = "servicos"

    id = Column(Integer, primary_key=True, index=True)
    escritorio_id = Column(Integer, ForeignKey("escritorios.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    tipo_servico_id = Column(Integer, ForeignKey("tipos_servico.id"), nullable=True)
    processo_id = Column(Integer, ForeignKey("processos.id"), nullable=True)
    descricao = Column(Text)
    status = Column(String(50), default='Ativo')
    
    # Dados Financeiros
    valor_total = Column(Float)
    condicoes_pagamento = Column(Text) # JSON com detalhes
    forma_pagamento = Column(String(100))
    qtd_parcelas = Column(Integer)
    detalhes_pagamento = Column(Text)
    porcentagem_exito = Column(String(20))
    data_contrato = Column(String(20))
    
    data_contratacao = Column(DateTime, default=func.now())

    escritorio = relationship("Escritorio")
    cliente = relationship("Cliente", back_populates="servicos")
    processo = relationship("Processo", back_populates="servicos", foreign_keys=[processo_id])
    tipo_servico = relationship("TipoServico")

class ModeloDocumento(Base):
    __tablename__ = "modelos_documento"

    id = Column(Integer, primary_key=True, index=True)
    escritorio_id = Column(Integer, ForeignKey("escritorios.id"), nullable=False, index=True)
    nome = Column(String(200), nullable=False)
    arquivo_path = Column(String(300), nullable=False)
    tamanho = Column(Integer, nullable=True) # em bytes
    data_criacao = Column(DateTime, default=func.now())
    data_alteracao = Column(DateTime, default=func.now(), onupdate=func.now())
    
    escritorio = relationship("Escritorio")

class PastaDocumento(Base):
    __tablename__ = "pastas_documento"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    escritorio_id = Column(Integer, ForeignKey("escritorios.id"), nullable=False, index=True)
    
    # Vínculos Opcionais
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True, index=True)
    servico_id = Column(Integer, ForeignKey("servicos.id"), nullable=True, index=True)
    processo_id = Column(Integer, ForeignKey("processos.id"), nullable=True, index=True)
    
    # Subpastas
    parent_id = Column(Integer, ForeignKey("pastas_documento.id"), nullable=True, index=True)

    data_criacao = Column(DateTime, default=func.now())
    
    escritorio = relationship("Escritorio")
    cliente = relationship("Cliente")
    servico = relationship("Servico")
    processo = relationship("Processo")
    subpastas = relationship("PastaDocumento", backref="parent", remote_side=[id])
    documentos = relationship("DocumentoCliente", back_populates="pasta")

class DocumentoCliente(Base):
    __tablename__ = "documentos_cliente"

    id = Column(Integer, primary_key=True, index=True)
    escritorio_id = Column(Integer, ForeignKey("escritorios.id"), nullable=False, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True, index=True)
    pasta_id = Column(Integer, ForeignKey("pastas_documento.id"), nullable=True, index=True)
    nome = Column(String(200), nullable=False)
    arquivo_path = Column(String(300), nullable=False)
    tamanho = Column(Integer, nullable=True) # em bytes
    data_criacao = Column(DateTime, default=func.now())
    data_alteracao = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # ADVtools Sign Fields
    token_assinatura = Column(String(32), unique=True, index=True, nullable=True) # UUID hex para acesso se precisar de sala pública do doc
    status_assinatura = Column(String(50), default="Aguardando") # Aguardando, Parcial, Concluido, Cancelado
    arquivo_assinado_path = Column(String(500), nullable=True) # Guarda o PDF final com as assinaturas e certificado
    hash_original = Column(String(64), nullable=True) # SHA256 do doc inicial
    hash_assinado = Column(String(64), nullable=True) # SHA256 do doc com manifesto
    token_validacao = Column(String(32), unique=True, index=True, nullable=True) # UUID hex para o QRCode
    
    escritorio = relationship("Escritorio")
    cliente = relationship("Cliente", back_populates="documentos")
    pasta = relationship("PastaDocumento", back_populates="documentos")
    signatarios = relationship("Signatario", back_populates="documento", cascade="all, delete-orphan", lazy="selectin")

class Signatario(Base):
    __tablename__ = "signatarios"

    id = Column(Integer, primary_key=True, index=True)
    documento_id = Column(Integer, ForeignKey("documentos_cliente.id"), nullable=False, index=True)
    token_acesso = Column(String(32), unique=True, index=True, nullable=False) # UUID hex
    nome = Column(String(200), nullable=False)
    email = Column(String(150), nullable=False)
    cpf = Column(String(20), nullable=True)
    funcao = Column(String(100), default="Parte") # Testemunha, Parte, Advogado
    
    status = Column(String(50), default="Pendente") # Pendente, Visualizado, Assinado
    data_visualizacao = Column(DateTime, nullable=True)
    data_assinatura = Column(DateTime, nullable=True)
    
    ip_assinatura = Column(String(50), nullable=True)
    user_agent_assinatura = Column(String(500), nullable=True)
    tipo_autenticacao = Column(String(50), nullable=True) # assinatura, selfie
    imagem_assinatura_path = Column(String(300), nullable=True)
    
    # ADVtools Sign Position Fields (Legacy - deprecated in favor of posicoes table)
    page_number = Column(Integer, nullable=True)
    x_pos = Column(Float, nullable=True)
    y_pos = Column(Float, nullable=True)
    width = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    docWidth = Column("docwidth", Float, nullable=True)
    docHeight = Column("docheight", Float, nullable=True)

    documento = relationship("DocumentoCliente", back_populates="signatarios")
    posicoes = relationship("SignatarioPosicao", back_populates="signatario", cascade="all, delete-orphan", lazy="selectin")

class SignatarioPosicao(Base):
    __tablename__ = "signatarios_posicoes"

    id = Column(Integer, primary_key=True, index=True)
    signatario_id = Column(Integer, ForeignKey("signatarios.id", ondelete="CASCADE"), nullable=False, index=True)
    page_number = Column(Integer, nullable=False)
    x_pos = Column(Float, nullable=False)
    y_pos = Column(Float, nullable=False)
    width = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    docWidth = Column("docwidth", Float, nullable=False)
    docHeight = Column("docheight", Float, nullable=False)

    signatario = relationship("Signatario", back_populates="posicoes")


class Processo(Base):
    __tablename__ = "processos"

    id = Column(Integer, primary_key=True, index=True)
    escritorio_id = Column(Integer, ForeignKey("escritorios.id"), nullable=False, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True, index=True)
    advogado_responsavel_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    pasta_trabalho_id = Column(Integer, ForeignKey("pastas_trabalho.id"), nullable=True)

    # Dados DataJud (Capa)
    numero_processo = Column(String(50), index=True) # Formato CNJ
    tribunal = Column(String(20)) # Sigla (TJSP, TRF3, etc)
    grau = Column(String(5), default='G1')
    data_ajuizamento = Column(DateTime, nullable=True)
    nivel_sigilo = Column(Integer, default=0)
    classe_codigo = Column(Integer)
    classe_nome = Column(String(255))
    orgao_julgador_codigo = Column(Integer)
    orgao_julgador_nome = Column(String(255))
    orgao_julgador_municipio_ibge = Column(Integer)
    formato_codigo = Column(Integer)
    formato_nome = Column(String(100), default='Eletrônico')
    sistema_codigo = Column(Integer)
    sistema_nome = Column(String(100))

    # Dados Internos
    titulo = Column(String(255), nullable=False)
    descricao = Column(Text)
    status = Column(String(50), default='Ativo')
    prioridade = Column(String(50), default='Normal')
    valor_causa = Column(Float)
    area_direito = Column(String(100))
    fase_processual = Column(String(100))
    polo = Column(String(50), default='Autor') # Polo que o escritório representa

    data_criacao = Column(DateTime, default=func.now())
    data_atualizacao = Column(DateTime, default=func.now(), onupdate=func.now())

    escritorio = relationship("Escritorio")
    cliente = relationship("Cliente")
    advogado_responsavel = relationship("Usuario")
    servico_id = Column(Integer, ForeignKey("servicos.id", ondelete="SET NULL"), nullable=True)
    servico = relationship("Servico", foreign_keys=[servico_id])
    servicos = relationship("Servico", back_populates="processo", foreign_keys="[Servico.processo_id]")
    partes = relationship("ProcessoParte", back_populates="processo", cascade="all, delete-orphan")
    assuntos = relationship("ProcessoAssunto", back_populates="processo", cascade="all, delete-orphan")
    movimentacoes = relationship("Movimentacao", back_populates="processo", cascade="all, delete-orphan")
    tarefas = relationship("Tarefa", back_populates="processo", cascade="all, delete-orphan")
    pasta_trabalho = relationship("PastaTrabalho")


class ProcessoParte(Base):
    __tablename__ = "processo_partes"

    id = Column(Integer, primary_key=True, index=True)
    processo_id = Column(Integer, ForeignKey("processos.id", ondelete="CASCADE"), nullable=False)
    tipo_parte = Column(String(100), nullable=False) # Polo Ativo, Polo Passivo, etc
    nome = Column(String(255), nullable=False)
    cpf_cnpj = Column(String(50))
    tipo_pessoa = Column(String(50), default='Física')
    advogado_nome = Column(String(255))
    advogado_oab = Column(String(50))

    processo = relationship("Processo", back_populates="partes")


class ProcessoAssunto(Base):
    __tablename__ = "processo_assuntos"

    id = Column(Integer, primary_key=True, index=True)
    processo_id = Column(Integer, ForeignKey("processos.id", ondelete="CASCADE"), nullable=False)
    codigo_tpu = Column(Integer)
    nome = Column(String(255), nullable=False)
    principal = Column(Boolean, default=False)

    processo = relationship("Processo", back_populates="assuntos")


class Movimentacao(Base):
    __tablename__ = "movimentacoes"

    id = Column(Integer, primary_key=True, index=True)
    processo_id = Column(Integer, ForeignKey("processos.id", ondelete="CASCADE"), nullable=False)
    tipo = Column(String(50), nullable=False) # externa (DataJud), interna (Escritório)
    codigo_movimento = Column(Integer)
    nome_movimento = Column(String(255), nullable=False)
    complementos_json = Column(Text) # Detalhes da movimentação
    descricao = Column(Text)
    orgao_julgador_codigo = Column(Integer)
    orgao_julgador_nome = Column(String(255))
    data_hora = Column(DateTime, nullable=False)
    data_registro = Column(DateTime, default=func.now())
    registrado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    processo = relationship("Processo", back_populates="movimentacoes")
    registrado_por = relationship("Usuario")

class Tarefa(Base):
    __tablename__ = "tarefas"

    id = Column(Integer, primary_key=True, index=True)
    escritorio_id = Column(Integer, ForeignKey("escritorios.id"), nullable=False, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True, index=True)
    processo_id = Column(Integer, ForeignKey("processos.id"), nullable=True, index=True)
    responsavel_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True, index=True)
    criado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    
    titulo = Column(String(255), nullable=False)
    descricao = Column(Text)
    status = Column(String(50), default="Pendente") # Pendente, Em Andamento, Concluída, Cancelada
    prioridade = Column(String(50), default="Normal") # Baixa, Normal, Alta, Urgente
    data_vencimento = Column(DateTime, nullable=True)
    
    data_criacao = Column(DateTime, default=func.now())
    data_atualizacao = Column(DateTime, default=func.now(), onupdate=func.now())

    escritorio = relationship("Escritorio")
    cliente = relationship("Cliente")
    processo = relationship("Processo", back_populates="tarefas")
    responsavel = relationship("Usuario", foreign_keys=[responsavel_id])
    criado_por = relationship("Usuario", foreign_keys=[criado_por_id])


class CategoriaFinanceira(Base):
    __tablename__ = "categorias_financeiras"
    id = Column(Integer, primary_key=True, index=True)
    escritorio_id = Column(Integer, ForeignKey("escritorios.id", ondelete="CASCADE"))
    tipo = Column(String) # Receita ou Despesa
    nome = Column(String)
    data_criacao = Column(DateTime, default=func.now())

    escritorio = relationship("Escritorio")

class Recorrencia(Base):
    __tablename__ = "recorrencias"

    id = Column(Integer, primary_key=True, index=True)
    escritorio_id = Column(Integer, ForeignKey("escritorios.id"), nullable=False, index=True)
    
    tipo = Column(String(20), nullable=False) # Receita, Despesa
    categoria = Column(String(100), nullable=False)
    valor = Column(Float, nullable=False)
    descricao = Column(Text)
    frequencia = Column(String(50), default="Mensal") # Mensal, Semanal, etc
    data_inicio = Column(DateTime, nullable=False)
    data_fim = Column(DateTime, nullable=True) # Se null, é "infinito" ou controlado por outro meio
    
    data_criacao = Column(DateTime, default=func.now())
    
    escritorio = relationship("Escritorio")
    transacoes = relationship("Transacao", back_populates="recorrencia", cascade="all, delete-orphan")


class Transacao(Base):
    __tablename__ = "transacoes"

    id = Column(Integer, primary_key=True, index=True)
    escritorio_id = Column(Integer, ForeignKey("escritorios.id"), nullable=False, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True, index=True)
    processo_id = Column(Integer, ForeignKey("processos.id"), nullable=True, index=True)
    servico_id = Column(Integer, ForeignKey("servicos.id", ondelete="SET NULL"), nullable=True, index=True)
    recorrencia_id = Column(Integer, ForeignKey("recorrencias.id", ondelete="CASCADE"), nullable=True, index=True)

    tipo = Column(String(20), nullable=False) # Receita, Despesa
    categoria = Column(String(100), nullable=False) # Honorários, Aluguel, etc
    valor = Column(Float, nullable=False)
    descricao = Column(Text)
    status = Column(String(50), default="Pendente") # Pendente, Pago, Atrasado, Cancelado
    
    data_vencimento = Column(DateTime, nullable=False)
    data_pagamento = Column(DateTime, nullable=True)
    forma_pagamento = Column(String(100))
    
    data_criacao = Column(DateTime, default=func.now())
    data_atualizacao = Column(DateTime, default=func.now(), onupdate=func.now())

    escritorio = relationship("Escritorio")
    cliente = relationship("Cliente")
    processo = relationship("Processo")
    servico = relationship("Servico")
    recorrencia = relationship("Recorrencia", back_populates="transacoes")
