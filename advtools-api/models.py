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


class Servico(Base):
    __tablename__ = "servicos"

    id = Column(Integer, primary_key=True, index=True)
    escritorio_id = Column(Integer, ForeignKey("escritorios.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    tipo_servico_id = Column(Integer, nullable=True) # Optional foreign key later
    processo_id = Column(Integer, nullable=True) # Optional foreign key later
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

class ModeloDocumento(Base):
    __tablename__ = "modelos_documento"

    id = Column(Integer, primary_key=True, index=True)
    escritorio_id = Column(Integer, ForeignKey("escritorios.id"), nullable=False, index=True)
    nome = Column(String(200), nullable=False)
    arquivo_path = Column(String(300), nullable=False)
    data_criacao = Column(DateTime, default=func.now())
    
    escritorio = relationship("Escritorio")

class DocumentoCliente(Base):
    __tablename__ = "documentos_cliente"

    id = Column(Integer, primary_key=True, index=True)
    escritorio_id = Column(Integer, ForeignKey("escritorios.id"), nullable=False, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False, index=True)
    nome = Column(String(200), nullable=False)
    arquivo_path = Column(String(300), nullable=False)
    data_criacao = Column(DateTime, default=func.now())
    
    # ADVtools Sign Fields
    token_assinatura = Column(String(32), unique=True, index=True, nullable=True) # UUID hex para acesso se precisar de sala pública do doc
    status_assinatura = Column(String(50), default="Aguardando") # Aguardando, Parcial, Concluido, Cancelado
    arquivo_assinado_path = Column(String(500), nullable=True) # Guarda o PDF final com as assinaturas e certificado
    hash_original = Column(String(64), nullable=True) # SHA256 do doc inicial
    hash_assinado = Column(String(64), nullable=True) # SHA256 do doc com manifesto
    token_validacao = Column(String(32), unique=True, index=True, nullable=True) # UUID hex para o QRCode
    
    escritorio = relationship("Escritorio")
    cliente = relationship("Cliente", back_populates="documentos")
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
    
    # ADVtools Sign Position Fields
    page_number = Column(Integer, nullable=True)
    x_pos = Column(Float, nullable=True)
    y_pos = Column(Float, nullable=True)
    width = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    docWidth = Column("docwidth", Float, nullable=True)
    docHeight = Column("docheight", Float, nullable=True)

    documento = relationship("DocumentoCliente", back_populates="signatarios")
