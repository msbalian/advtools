from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime

# ==========================
# Escritório (Office) Schema
# ==========================
class EscritorioBase(BaseModel):
    nome: str
    documento: Optional[str] = None

class EscritorioCreate(EscritorioBase):
    pass

class EscritorioUpdate(BaseModel):
    nome: Optional[str] = None
    documento: Optional[str] = None
    logo_path: Optional[str] = None
    gemini_api_key: Optional[str] = None

class Escritorio(EscritorioBase):
    id: int
    logo_path: Optional[str] = None
    gemini_api_key: Optional[str] = None
    data_criacao: datetime

    class Config:
        from_attributes = True

# ==========================
# Usuário (User) Schema
# ==========================
class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr
    tipo: str = "Humano"
    perfil: str = "Colaborador"
    cpf: Optional[str] = None
    ativo: bool = True
    is_admin: bool = False

class UsuarioCreate(UsuarioBase):
    senha: str
    escritorio_id: Optional[int] = None

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    senha: Optional[str] = None
    tipo: Optional[str] = None
    perfil: Optional[str] = None
    cpf: Optional[str] = None
    ativo: Optional[bool] = None
    is_admin: Optional[bool] = None

class Usuario(UsuarioBase):
    id: int
    escritorio_id: int
    data_criacao: datetime
    
    class Config:
        from_attributes = True

# ==========================
# Login / Auth Schemas
# ==========================
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# ==========================
# Cliente Schema
# ==========================
class ClienteBase(BaseModel):
    nome: str
    documento: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None
    endereco: Optional[str] = None
    cep: Optional[str] = None
    data_nascimento: Optional[str] = None
    nacionalidade: Optional[str] = None
    estado_civil: Optional[str] = None
    profissao: Optional[str] = None
    rg: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    uf: Optional[str] = None

    @field_validator("email", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        return None if v == "" else v

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(ClienteBase):
    nome: Optional[str] = None

class Cliente(ClienteBase):
    id: int
    escritorio_id: int
    data_cadastro: datetime

    class Config:
        from_attributes = True

# ==========================
# Servico / Contrato Schema
# ==========================
class ServicoBase(BaseModel):
    cliente_id: int
    tipo_servico_id: Optional[int] = None
    processo_id: Optional[int] = None
    descricao: Optional[str] = None
    status: str = "Ativo"
    valor_total: Optional[float] = None
    condicoes_pagamento: Optional[str] = None
    forma_pagamento: Optional[str] = None
    qtd_parcelas: Optional[int] = None
    detalhes_pagamento: Optional[str] = None
    porcentagem_exito: Optional[str] = None
    data_contrato: Optional[str] = None

class ServicoCreate(ServicoBase):
    pass

class ServicoUpdate(ServicoBase):
    cliente_id: Optional[int] = None

class Servico(ServicoBase):
    id: int
    cliente_id: int
    escritorio_id: int
    data_contratacao: datetime

    class Config:
        from_attributes = True

# ==========================
# PARTES ENVOLVIDAS
# ==========================
class ParteEnvolvidaBase(BaseModel):
    nome: str
    documento: Optional[str] = None
    papel: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    rg: Optional[str] = None
    data_nascimento: Optional[str] = None
    nacionalidade: Optional[str] = None
    estado_civil: Optional[str] = None
    profissao: Optional[str] = None
    cep: Optional[str] = None
    endereco: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    uf: Optional[str] = None

    @field_validator("email", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        return None if v == "" else v

class ParteEnvolvidaCreate(ParteEnvolvidaBase):
    cliente_id: int
    escritorio_id: Optional[int] = None

class ParteEnvolvidaUpdate(BaseModel):
    nome: Optional[str] = None
    documento: Optional[str] = None
    papel: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    rg: Optional[str] = None
    data_nascimento: Optional[str] = None
    nacionalidade: Optional[str] = None
    estado_civil: Optional[str] = None
    profissao: Optional[str] = None
    cep: Optional[str] = None
    endereco: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    uf: Optional[str] = None

    @field_validator("email", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        return None if v == "" else v

class ParteEnvolvida(ParteEnvolvidaBase):
    id: int
    cliente_id: int
    escritorio_id: int
    data_cadastro: datetime

    class Config:
        from_attributes = True

# ==========================
# DOCUMENTOS DO CLIENTE & ASSINATURAS
# ==========================
class SignatarioBase(BaseModel):
    nome: str
    email: EmailStr
    cpf: Optional[str] = None
    funcao: Optional[str] = "Parte"

class SignatarioCreate(SignatarioBase):
    pass

class SignatarioPosicaoItem(BaseModel):
    page_number: int
    x_pos: float
    y_pos: float
    width: float
    height: float
    docWidth: float
    docHeight: float

    class Config:
        from_attributes = True

class SignatarioResponse(SignatarioBase):
    id: int
    documento_id: int
    token_acesso: str
    status: str
    data_visualizacao: Optional[datetime]
    data_assinatura: Optional[datetime]
    tipo_autenticacao: Optional[str]
    posicoes: List[SignatarioPosicaoItem] = []
    # Nao retornamos paths internos pro frontend publico, apenas infos publicaveis

    class Config:
        from_attributes = True

class SignatarioPosicoesUpdate(BaseModel):
    posicoes: List[SignatarioPosicaoItem]

class AssinaturaConfirmarRequest(BaseModel):
    imagem_base64: str
    cpf: Optional[str] = None
    tipo_autenticacao: str # 'assinatura' ou 'selfie'
    
    # Coordenadas visuais (para pdf)
    pos_x: Optional[float] = None
    pos_y: Optional[float] = None
    pos_width: Optional[float] = None
    pos_height: Optional[float] = None
    pos_page: Optional[int] = None
    pos_doc_width: Optional[float] = None
    pos_doc_height: Optional[float] = None

class DocumentoClienteBase(BaseModel):
    nome: str

class DocumentoClienteCreate(DocumentoClienteBase):
    cliente_id: int

class DocumentoCliente(DocumentoClienteBase):
    id: int
    escritorio_id: int
    cliente_id: int
    arquivo_path: str
    arquivo_assinado_path: Optional[str] = None
    data_criacao: datetime
    
    # ADVtools Sign Fields
    token_assinatura: Optional[str] = None
    status_assinatura: Optional[str] = "Aguardando"
    hash_original: Optional[str] = None
    hash_assinado: Optional[str] = None
    token_validacao: Optional[str] = None
    
    signatarios: List[SignatarioResponse] = []

    class Config:
        from_attributes = True

# Form request schema para o Redator Inteligente
class GerarDocumentoRequest(BaseModel):
    cliente_id: int
    modelo_id: int
    titulo_documento: str
    usar_ia: bool = False
    instrucoes_ia: Optional[str] = None
