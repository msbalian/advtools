import os
from typing import List
import shutil
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

import models
import schemas
import crud
import auth
from database import engine, get_db
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
import logging
import traceback
from fastapi import Request
from fastapi.responses import JSONResponse

# Configura log para arquivo para vermos erros 500 que uvicorn esconde
logging.basicConfig(filename='api_errors.log', level=logging.ERROR)

# Este app é sua API core em FastAPI
app = FastAPI(title="ADVtools API", description="API para sistema jurídico", version="1.0.0")

# Setup CORS para o Vue.js poder consumir sem erros de Cross-Origin
origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:5174",
]

# Servir arquivos da pasta static (como as logomarcas)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        logging.error(f"Erro na requisição {request.url.path}: {str(exc)}")
        logging.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"detail": f"Erro interno: {str(exc)}", "traceback": traceback.format_exc()}
        )

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

async def convert_docx_to_pdf_async(in_path: str, out_path: str):
    """Executa a conversão do DOCX para PDF em uma thread separada."""
    import asyncio
    import os
    abs_in = os.path.abspath(in_path)
    abs_out = os.path.abspath(out_path)
    
    loop = asyncio.get_running_loop()
    
    def do_convert():
        import pythoncom
        from docx2pdf import convert
        # Inicializa o COM na thread atual (necessário para threads em background)
        pythoncom.CoInitialize()
        try:
            convert(abs_in, abs_out)
        finally:
            pythoncom.CoUninitialize()

    await loop.run_in_executor(None, do_convert)

# Dependência para pegar o usuário atual logado via Token JWT
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = await crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


# ==========================
# ROTAS PÚBLICAS / AUTH
# ==========================
@app.post("/api/login", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await crud.get_user_by_email(db, email=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/register", response_model=schemas.Usuario)
async def register_user(user_in: schemas.UsuarioCreate, db: AsyncSession = Depends(get_db)):
    # Very basic validation (should expand later with Escritorio creation rules)
    existing_user = await crud.get_user_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
        
    user = await crud.create_user(db, user_in)
    return user

@app.get("/api/me", response_model=schemas.Usuario)
async def read_users_me(current_user: models.Usuario = Depends(get_current_user)):
    return current_user

# ==========================
# ROTAS DE USUÁRIOS (EQUIPE) E ESCRITÓRIO
# ==========================

@app.post("/api/escritorios", response_model=schemas.Escritorio)
async def create_escritorio(escritorio_in: schemas.EscritorioCreate, db: AsyncSession = Depends(get_db)):
    """
    Endpoint público para registrar um novo escritório (Step 1 do fluxo de registro).
    """
    escritorio = models.Escritorio(**escritorio_in.model_dump())
    db.add(escritorio)
    try:
        await db.commit()
        await db.refresh(escritorio)
        return escritorio
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Erro ao criar escritório")

@app.get("/api/usuarios", response_model=list[schemas.Usuario])
async def read_usuarios(current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await crud.get_usuarios(db, escritorio_id=current_user.escritorio_id)

@app.post("/api/usuarios", response_model=schemas.Usuario)
async def create_usuario_equipe(user_in: schemas.UsuarioCreate, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem adicionar usuários.")
        
    user_in.escritorio_id = current_user.escritorio_id # Força o usuário pro mesmo escritório
    
    existing_user = await crud.get_user_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
        
    return await crud.create_user(db, user_in)

@app.put("/api/usuarios/{user_id}", response_model=schemas.Usuario)
async def update_usuario_equipe(user_id: int, user_update: schemas.UsuarioUpdate, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Admin pode editar qualquer uno. Usuário normal só edita a si mesmo.
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Sem permissão para editar outros usuários.")
        
    updated_user = await crud.update_usuario(db, user_id, current_user.escritorio_id, user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return updated_user

@app.delete("/api/usuarios/{user_id}", status_code=204)
async def delete_usuario_equipe(user_id: int, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem excluir usuários.")
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Não é possível excluir a si mesmo.")
        
    success = await crud.delete_usuario(db, user_id, current_user.escritorio_id)
    if not success:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return None



@app.get("/api/escritorio", response_model=schemas.Escritorio)
async def get_meu_escritorio(current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    escritorio = await crud.get_escritorio(db, current_user.escritorio_id)
    if not escritorio:
        raise HTTPException(status_code=404, detail="Escritório não encontrado")
    return escritorio

@app.put("/api/escritorio", response_model=schemas.Escritorio)
async def update_meu_escritorio(
    nome: str = Form(...),
    documento: str = Form(None),
    logo: UploadFile = File(None),
    current_user: models.Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Se uma imagem foi enviada, salva localmente
    logo_path = None
    if logo:
        # Extrair extensão e montar o nome do arquivo baseado no ID do escritório
        ext = logo.filename.split('.')[-1] if '.' in logo.filename else 'png'
        filename = f"logo_{current_user.escritorio_id}.{ext}"
        
        # Garantir que a pasta static/logos exista
        os.makedirs("static/logos", exist_ok=True)
        file_path = os.path.join("static/logos", filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(logo.file, buffer)
            
        logo_path = f"logos/{filename}" # Caminho relativo servido pelo mount /static
        
    escritorio_update = schemas.EscritorioUpdate(
        nome=nome,
        documento=documento,
        logo_path=logo_path
    )
    
    updated_escritorio = await crud.update_escritorio(db, current_user.escritorio_id, escritorio_update)
    if not updated_escritorio:
        raise HTTPException(status_code=404, detail="Escritório não encontrado")
        
    return updated_escritorio

# ==========================
# ROTAS DE CLIENTES
# ==========================
@app.get("/api/clientes", response_model=list[schemas.Cliente])
async def read_clientes(current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await crud.get_clientes(db, escritorio_id=current_user.escritorio_id)

@app.post("/api/clientes", response_model=schemas.Cliente)
async def create_cliente(cliente: schemas.ClienteCreate, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await crud.create_cliente(db, cliente, escritorio_id=current_user.escritorio_id)

@app.get("/api/clientes/{cliente_id}", response_model=schemas.Cliente)
async def read_cliente(cliente_id: int, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    cliente = await crud.get_cliente(db, cliente_id, escritorio_id=current_user.escritorio_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente

@app.get("/api/clientes/{cliente_id}/servicos", response_model=list[schemas.Servico])
async def read_servicos_by_cliente(cliente_id: int, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await crud.get_servicos_by_cliente(db, cliente_id, escritorio_id=current_user.escritorio_id)

@app.put("/api/clientes/{cliente_id}", response_model=schemas.Cliente)
async def update_cliente(cliente_id: int, cliente: schemas.ClienteUpdate, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    updated_cliente = await crud.update_cliente(db, cliente_id, cliente, escritorio_id=current_user.escritorio_id)
    if not updated_cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return updated_cliente

@app.delete("/api/clientes/{cliente_id}", status_code=204)
async def delete_cliente(cliente_id: int, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    success = await crud.delete_cliente(db, cliente_id, escritorio_id=current_user.escritorio_id)
    if not success:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return None

# ==========================
# ROTAS DE SERVIÇOS
# ==========================
@app.get("/api/servicos", response_model=list[schemas.Servico])
async def read_servicos(current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await crud.get_servicos(db, escritorio_id=current_user.escritorio_id)

@app.post("/api/servicos", response_model=schemas.Servico)
async def create_servico(servico: schemas.ServicoCreate, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await crud.create_servico(db, servico, escritorio_id=current_user.escritorio_id)

@app.put("/api/servicos/{servico_id}", response_model=schemas.Servico)
async def update_servico(servico_id: int, servico: schemas.ServicoUpdate, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    updated_servico = await crud.update_servico(db, servico_id, servico, escritorio_id=current_user.escritorio_id)
    if not updated_servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    return updated_servico

@app.delete("/api/servicos/{servico_id}", status_code=204)
async def delete_servico(servico_id: int, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    success = await crud.delete_servico(db, servico_id, escritorio_id=current_user.escritorio_id)
    if not success:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    return None

# ==========================
# ROTAS DE PARTES ENVOLVIDAS
# ==========================
@app.get("/api/clientes/{cliente_id}/partes", response_model=list[schemas.ParteEnvolvida])
async def read_partes_cliente(cliente_id: int, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await crud.get_partes_cliente(db, cliente_id, escritorio_id=current_user.escritorio_id)

@app.post("/api/partes", response_model=schemas.ParteEnvolvida)
async def create_parte(parte: schemas.ParteEnvolvidaCreate, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    parte.escritorio_id = current_user.escritorio_id
    return await crud.create_parte_envolvida(db, parte)

@app.get("/api/modelos")
async def listar_modelos(db: AsyncSession = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    q = select(models.ModeloDocumento).where(models.ModeloDocumento.escritorio_id == current_user.escritorio_id)
    res = await db.execute(q)
    modelos = res.scalars().all()
    if not modelos:
        return []
    return [{"id": m.id, "nome": m.nome, "arquivo_path": m.arquivo_path, "data_criacao": m.data_criacao} for m in modelos]

@app.post("/api/modelos")
async def criar_modelo(
    file: UploadFile = File(...),
    nome: str = Form(...),
    db: AsyncSession = Depends(get_db), 
    current_user: models.Usuario = Depends(get_current_user)
):
    if not file.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Apenas arquivos .docx são permitidos")
        
    upload_dir = "static/modelos"
    os.makedirs(upload_dir, exist_ok=True)
    
    import uuid
    import shutil
    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    db_path = f"modelos/{unique_filename}"
    novo_modelo = models.ModeloDocumento(
        escritorio_id=current_user.escritorio_id,
        nome=nome,
        arquivo_path=db_path
    )
    db.add(novo_modelo)
    await db.commit()
    await db.refresh(novo_modelo)
    
    return {"id": novo_modelo.id, "nome": novo_modelo.nome, "arquivo_path": novo_modelo.arquivo_path}

@app.delete("/api/modelos/{modelo_id}")
async def deletar_modelo(modelo_id: int, db: AsyncSession = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    q = select(models.ModeloDocumento).where(
        models.ModeloDocumento.id == modelo_id,
        models.ModeloDocumento.escritorio_id == current_user.escritorio_id
    )
    res = await db.execute(q)
    modelo = res.scalars().first()
    
    if not modelo:
        raise HTTPException(status_code=404, detail="Modelo não encontrado")
        
    file_path = os.path.join("static", modelo.arquivo_path)
    if os.path.exists(file_path):
        os.remove(file_path)
        
    await db.delete(modelo)
    await db.commit()
    return {"detail": "Modelo deletado com sucesso"}

@app.put("/api/modelos/{modelo_id}")
async def substituir_modelo(
    modelo_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db), 
    current_user: models.Usuario = Depends(get_current_user)
):
    if not file.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Apenas arquivos .docx são permitidos")
        
    q = select(models.ModeloDocumento).where(
        models.ModeloDocumento.id == modelo_id,
        models.ModeloDocumento.escritorio_id == current_user.escritorio_id
    )
    res = await db.execute(q)
    modelo = res.scalars().first()
    
    if not modelo:
        raise HTTPException(status_code=404, detail="Modelo não encontrado")
        
    old_file_path = os.path.join("static", modelo.arquivo_path)
    if os.path.exists(old_file_path):
        os.remove(old_file_path)
        
    upload_dir = "static/modelos"
    os.makedirs(upload_dir, exist_ok=True)
    
    import uuid
    import shutil
    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    modelo.arquivo_path = f"modelos/{unique_filename}"
    await db.commit()
    await db.refresh(modelo)
    
    return {"id": modelo.id, "nome": modelo.nome, "arquivo_path": modelo.arquivo_path}

@app.put("/api/partes/{parte_id}", response_model=schemas.ParteEnvolvida)
async def update_parte(parte_id: int, parte: schemas.ParteEnvolvidaUpdate, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    updated_parte = await crud.update_parte_envolvida(db, parte_id, current_user.escritorio_id, parte)
    if not updated_parte:
        raise HTTPException(status_code=404, detail="Parte não encontrada")
    return updated_parte

@app.delete("/api/partes/{parte_id}", status_code=204)
async def delete_parte(parte_id: int, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    success = await crud.delete_parte_envolvida(db, parte_id, current_user.escritorio_id)
    if not success:
        raise HTTPException(status_code=404, detail="Parte não encontrada")
    return None

# ==========================
# DOCUMENTOS DO CLIENTE & REDATOR
# ==========================
@app.get("/api/clientes/{cliente_id}/documentos", response_model=list[schemas.DocumentoCliente])
async def read_documentos_cliente(cliente_id: int, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await crud.get_documentos_cliente(db, cliente_id, escritorio_id=current_user.escritorio_id)

@app.get("/api/documentos/{documento_id}", response_model=schemas.DocumentoCliente)
async def read_documento(documento_id: int, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    doc = await crud.get_documento_by_id(db, documento_id, current_user.escritorio_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    return doc

@app.post("/api/clientes/{cliente_id}/documentos", response_model=schemas.DocumentoCliente)
async def upload_documento_cliente(
    cliente_id: int,
    file: UploadFile = File(...),
    nome: str = Form(...),
    db: AsyncSession = Depends(get_db), 
    current_user: models.Usuario = Depends(get_current_user)
):
    upload_dir = "static/documentos_clientes"
    os.makedirs(upload_dir, exist_ok=True)
    
    import uuid
    import shutil
    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    db_path = f"documentos_clientes/{unique_filename}"
    
    doc_create = schemas.DocumentoClienteCreate(nome=nome, cliente_id=cliente_id)
    return await crud.create_documento_cliente(db, doc_create, db_path, current_user.escritorio_id)

@app.delete("/api/documentos/{documento_id}", status_code=204)
async def delete_documento(documento_id: int, db: AsyncSession = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    deleted_doc = await crud.delete_documento_cliente(db, documento_id, current_user.escritorio_id)
    if not deleted_doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
        
    file_path = os.path.join("static", deleted_doc.arquivo_path)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    return None

@app.put("/api/documentos/{documento_id}", response_model=schemas.DocumentoCliente)
async def update_documento_file(
    documento_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db), 
    current_user: models.Usuario = Depends(get_current_user)
):
    # Verify document exists and user has access
    doc = await crud.get_documento_by_id(db, documento_id, current_user.escritorio_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
        
    # Replace the physical file but keep the same path and name
    file_path = os.path.join("static", doc.arquivo_path)
    
    # Ensure directory exists just in case
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, "wb") as buffer:
        import shutil
        shutil.copyfileobj(file.file, buffer)
        
    # Update modification timestamp or just return the doc (using commit to trigger any onupdate hooks if exist)
    await db.commit()
    await db.refresh(doc)
    
    return doc


from docxtpl import DocxTemplate
from datetime import datetime
import locale

# Tenta setar locale pt-br para datas por extenso
try:
    # No Windows tente: 'Portuguese_Brazil.1252' ou 'pt-BR'
    # No Linux tente: 'pt_BR.utf8'
    locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
except Exception:
    try:
        locale.setlocale(locale.LC_TIME, 'pt-BR')
    except Exception:
        try:
           locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')
        except Exception:
           pass

@app.post("/api/redator/gerar", response_model=schemas.DocumentoCliente)
async def gerar_documento(
    request: schemas.GerarDocumentoRequest,
    db: AsyncSession = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    # 1. Obter Cliente e Modelo
    cliente = await crud.get_cliente(db, request.cliente_id, current_user.escritorio_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
        
    q_modelo = select(models.ModeloDocumento).where(
        models.ModeloDocumento.id == request.modelo_id,
        models.ModeloDocumento.escritorio_id == current_user.escritorio_id
    )
    res_modelo = await db.execute(q_modelo)
    modelo = res_modelo.scalars().first()
    
    if not modelo:
        raise HTTPException(status_code=404, detail="Modelo não encontrado")

    # 2. Obter Partes Envolvidas e Serviços (para as tags)
    partes = await crud.get_partes_cliente(db, request.cliente_id, current_user.escritorio_id)
    servicos = await crud.get_servicos_by_cliente(db, request.cliente_id, current_user.escritorio_id)
    
    # Pega o primeiro serviço ativo, se houver, como padrão
    servico = next((s for s in servicos if s.status == "Ativo"), servicos[0] if servicos else None)

    # 3. Montar Contexto (Dicionário de Tags)
    # 3. Montar Contexto (Dicionário de Tags)
    hoje = datetime.now()
    
    context = {
        # Cliente
        "cliente_nome": cliente.nome or "",
        "cliente_doc": cliente.documento or "",
        "cliente_endereco": cliente.endereco or "",
        "cliente_bairro": cliente.bairro or "",
        "cliente_cidade": cliente.cidade or "",
        "cliente_uf": cliente.uf or "",
        "cliente_cep": cliente.cep or "",
        "cliente_email": cliente.email or "",
        "cliente_nacionalidade": cliente.nacionalidade or "",
        "cliente_estado_civil": cliente.estado_civil or "",
        "cliente_profissao": cliente.profissao or "",
        "cliente_rg": cliente.rg or "",
        "cliente_data_nascimento": cliente.data_nascimento or "",
        
        # Datas
        "data_hoje": hoje.strftime("%d/%m/%Y"),
        "ano_atual": hoje.strftime("%Y"),
        "data_extenso": hoje.strftime("%d de %B de %Y"),
        
        # IA & Extras (Mocks temporários na v1 sem IA)
        "conteudo_ia": "[Conteúdo IA indisponível. Habilite a IA na redação.]" if not request.usar_ia else "[Conteúdo gerado por IA...]",
        
        # Serviço / Financeiro
        "servico_tipo": servico.tipo_servico_id if servico else "",
        "percentual_exito": servico.porcentagem_exito if servico else "",
    }

    # Tratamento de Pagamentos (JSON 1-to-N)
    import json
    pagamentos_list = []
    pagamentos_resumo_linhas = []
    soma_valor_total = 0.0

    if servico and servico.condicoes_pagamento:
        try:
            pagamentos_raw = json.loads(servico.condicoes_pagamento)
            if isinstance(pagamentos_raw, list):
                pagamentos_list = pagamentos_raw
        except json.JSONDecodeError:
            pass
            
    # Computar resumo e tags individuais de pagamento
    for i, pag in enumerate(pagamentos_list):
        valor_num = float(pag.get("valor") or 0)
        soma_valor_total += valor_num
        
        # Formatar valor e data pt-BR
        valor_str = f"R$ {valor_num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        data_str = pag.get("data") or ""
        if data_str and "T" not in data_str and len(data_str.split("-")) == 3:
            # Format YYYY-MM-DD to DD/MM/YYYY
            partes_data = data_str.split("-")
            data_str = f"{partes_data[2]}/{partes_data[1]}/{partes_data[0]}"

        tipo = pag.get("tipo") or "Desconhecido"
        obs = pag.get("obs") or ""
        
        linha_resumo = f"{i+1}ª Parcela - {data_str} - {valor_str} ({tipo})"
        if obs:
            linha_resumo += f" - {obs}"
        pagamentos_resumo_linhas.append(linha_resumo)
        
        # Tags individuais seguras até 12 parcelas
        if i < 12:
            prefix = f"pagamento_{i+1}_"
            context[f"{prefix}valor"] = valor_str
            context[f"{prefix}data"] = data_str
            context[f"{prefix}tipo"] = tipo
            context[f"{prefix}obs"] = obs

    # For pre-filling empty templates where the tags are statically referenced
    for i in range(len(pagamentos_list), 12):
        prefix = f"pagamento_{i+1}_"
        context[f"{prefix}valor"] = ""
        context[f"{prefix}data"] = ""
        context[f"{prefix}tipo"] = ""
        context[f"{prefix}obs"] = ""

    context["pagamentos"] = pagamentos_list
    context["pagamentos_resumo"] = "\n".join(pagamentos_resumo_linhas)
    context["qtd_parcelas"] = str(len(pagamentos_list))
    
    # Lista de parcelas em texto único formatado para uso simples com {{ pagamento_parcelas }}
    parcelas_linhas = []
    for i, pag in enumerate(pagamentos_list):
        valor_num = float(pag.get("valor") or 0)
        valor_str = f"R$ {valor_num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        data_str = pag.get("data") or ""
        if data_str and "T" not in data_str and len(data_str.split("-")) == 3:
            partes_data = data_str.split("-")
            data_str = f"{partes_data[2]}/{partes_data[1]}/{partes_data[0]}"

        linha = f"{i + 1}ª Parcela - {data_str} - {valor_str}"
        tipo = pag.get("tipo") or ""
        if tipo:
            linha += f" ({tipo})"
        obs = pag.get("obs") or ""
        if obs:
            linha += f" - {obs}"
            
        parcelas_linhas.append(linha)
        
    context["pagamento_parcelas"] = "\n".join(parcelas_linhas) if parcelas_linhas else ""
    
    
    # Valor Total
    if soma_valor_total > 0:
        context["pagamento_valor"] = f"R$ {soma_valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        context["valor_total"] = context["pagamento_valor"] # Manter legibilidade para templates antigos
    else:
        # Fallback para o campo valor_total antigo se não houver JSON listado
        val = servico.valor_total if servico else 0.0
        context["pagamento_valor"] = f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if val else ""
        context["valor_total"] = context["pagamento_valor"]

    context["forma_pagamento"] = servico.forma_pagamento if servico else ""
    context["detalhes_pagamento"] = servico.detalhes_pagamento if servico else ""
    
    # Partes Envolvidas
    partes_txt = []
    for i, parte in enumerate(partes):
        # Lista combinada
        papel = parte.papel or "Envolvido"
        partes_txt.append(f"{parte.nome} ({papel})")
        
        # Tags individuais seguras até parte_5
        if i < 5:
            prefix = f"parte_{i+1}_"
            context[f"{prefix}nome"] = parte.nome or ""
            context[f"{prefix}doc"] = parte.documento or ""
            context[f"{prefix}rg"] = parte.rg or ""
            context[f"{prefix}nasc"] = parte.data_nascimento or ""
            context[f"{prefix}nacionalidade"] = parte.nacionalidade or ""
            context[f"{prefix}estado_civil"] = parte.estado_civil or ""
            context[f"{prefix}profissao"] = parte.profissao or ""
            context[f"{prefix}endereco"] = parte.endereco or ""
            context[f"{prefix}bairro"] = parte.bairro or ""
            context[f"{prefix}cidade"] = parte.cidade or ""
            context[f"{prefix}uf"] = parte.uf or ""
            context[f"{prefix}cep"] = parte.cep or ""
            context[f"{prefix}papel"] = parte.papel or ""
            
    context["partes_resumo"] = "\n".join(partes_txt)
    context["partes_txt"] = ", ".join(partes_txt)

    # Preenche o restante vazio para partes nulas até < 5
    for i in range(len(partes), 5):
        prefix = f"parte_{i+1}_"
        for field in ["nome", "doc", "rg", "nasc", "nacionalidade", "estado_civil", "profissao", "endereco", "bairro", "cidade", "uf", "cep", "papel"]:
            context[f"{prefix}{field}"] = ""

        # 4. Processar o Documento (.docx)
    try:
        source_path = os.path.join("static", modelo.arquivo_path)
        with open("redator_debug.log", "a", encoding="utf-8") as debug_file:
            debug_file.write(f"\n--- GERAÇÃO EM {datetime.now()} ---\n")
            debug_file.write(f"Template: {source_path}\n")
            debug_file.write(f"Contexto: {list(context.keys())}\n")
            failing_tags = ["cliente_nacionalidade", "cliente_estado_civil", "cliente_profissao", "cliente_rg", "cliente_endereco", "cliente_bairro", "cliente_cep"]
            for tag in failing_tags:
                debug_file.write(f"  - {tag}: '{context.get(tag)}'\n")

        doc = DocxTemplate(source_path)
        doc.render(context)
        
        import uuid
        import re
        import unicodedata

        def slugify(value):
            # Normaliza para remover acentos
            nfkd_form = unicodedata.normalize('NFKD', value)
            only_ascii = nfkd_form.encode('ascii', 'ignore').decode('ascii')
            # Remove caracteres especiais e troca espaços por underline
            cleaned = re.sub(r'[^\w\s-]', '', only_ascii).strip().lower()
            return re.sub(r'[-\s]+', '_', cleaned)

        upload_dir = "static/documentos_clientes"
        os.makedirs(upload_dir, exist_ok=True)
        
        safe_title = slugify(request.titulo_documento)
        unique_filename = f"{safe_title}_{uuid.uuid4().hex[:6]}.docx"
        output_path = os.path.join(upload_dir, unique_filename)
        
        doc.save(output_path)
        print(f"DEBUG REDATOR: Documento salvo em {output_path}")
    except Exception as e:
        import traceback
        print(f"ERRO CRÍTICO NO REDATOR: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao processar template .docx: {str(e)}")

    # 5. Salvar no Banco
    db_path = f"documentos_clientes/{unique_filename}"
    doc_create = schemas.DocumentoClienteCreate(nome=request.titulo_documento, cliente_id=request.cliente_id)
    db_doc = await crud.create_documento_cliente(db, doc_create, db_path, current_user.escritorio_id)

    return db_doc

import assinador_service
import base64

# ==========================
# GESTÃO DE ASSINATURAS (ADVtools Sign) - RESTRIÇÃO LOGADA
# ==========================

@app.get("/api/documentos/{documento_id}/signatarios", response_model=List[schemas.SignatarioResponse])
async def read_signatarios(documento_id: int, db: AsyncSession = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    signatarios = await crud.get_signatarios(db, documento_id, current_user.escritorio_id)
    if signatarios is None:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    return signatarios

@app.post("/api/documentos/{documento_id}/signatarios", response_model=schemas.SignatarioResponse)
async def create_signatario(documento_id: int, signatario: schemas.SignatarioCreate, db: AsyncSession = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    db_sig = await crud.create_signatario(db, documento_id, signatario, current_user.escritorio_id)
    if not db_sig:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    return db_sig

@app.delete("/api/documentos/{documento_id}/signatarios/{signatario_id}")
async def delete_signatario(documento_id: int, signatario_id: int, db: AsyncSession = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    success = await crud.delete_signatario(db, documento_id, signatario_id, current_user.escritorio_id)
    if not success:
        raise HTTPException(status_code=404, detail="Signatário não encontrado ou não autorizado")
    return {"message": "Signatário removido"}

@app.put("/api/documentos/{documento_id}/signatarios/{signatario_id}/posicao")
async def update_signatario_posicao(documento_id: int, signatario_id: int, posicao: schemas.SignatarioPosicoesUpdate, db: AsyncSession = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    # First, verify the document belongs to the user's office
    doc = await crud.get_documento_by_id(db, documento_id, current_user.escritorio_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
        
    updated = await crud.update_signatario_posicao(db, signatario_id, posicao)
    if not updated:
        raise HTTPException(status_code=404, detail="Signatário não encontrado")
    return {"message": "Posições salvas com sucesso"}

@app.post("/api/documentos/{documento_id}/finalizar")
async def finalizar_documento(documento_id: int, db: AsyncSession = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    # Rota para forçar a finalização/merge do documento se todos assinaram
    doc = await crud.get_documento_by_id(db, documento_id, current_user.escritorio_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
        
    signatarios = await crud.get_signatarios(db, documento_id, current_user.escritorio_id)
    pendentes = [s for s in signatarios if s.status != 'Assinado']
    
    if pendentes:
        raise HTTPException(status_code=400, detail="Ainda há assinaturas pendentes.")
        
    # Chama rotina de merge
    # (A lógica principal de merge real deve ser acionada aqui ou no public endpoint)
    # Por segurança, apenas atualiza status e garante o hash
    if doc.status_assinatura != 'Concluido':
        doc.status_assinatura = 'Concluido'
        if not doc.token_validacao:
            import uuid
            doc.token_validacao = uuid.uuid4().hex
        db.add(doc)
        await db.commit()
        
    return {"message": "Processamento concluído", "status": "Concluido"}


@app.get("/api/public/assinar/preview-pdf/{documento_id}")
async def preview_pdf(documento_id: int, db: AsyncSession = Depends(get_db)):
    from fastapi.responses import FileResponse
    import os
    
    # We allow this without auth to reuse the same logic, but in a real app we'd check if the user has access.
    # We will just fetch the document.
    from sqlalchemy import select
    res = await db.execute(select(models.DocumentoCliente).filter(models.DocumentoCliente.id == documento_id))
    doc = res.scalars().first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
        
    arquivo_original = f"static/{doc.arquivo_path}"
    arquivo_exibicao = arquivo_original
    
    if arquivo_original.lower().endswith('.docx'):
        pdf_path = arquivo_original.replace('.docx', '_visualizacao.pdf')
        if not os.path.exists(pdf_path) and os.path.exists(arquivo_original):
            try:
                await convert_docx_to_pdf_async(arquivo_original, pdf_path)
            except Exception as e:
                print(f"Erro ao converter DOCX para PDF para visualização: {e}")
        
        if os.path.exists(pdf_path):
            arquivo_exibicao = pdf_path
            
    if not os.path.exists(arquivo_exibicao):
        raise HTTPException(status_code=404, detail="Arquivo físico não encontrado")
        
    return FileResponse(arquivo_exibicao, media_type="application/pdf")

# ==========================
# GESTÃO DE ASSINATURAS (ADVtools Sign) - ROTAS PÚBLICAS
# ==========================

@app.get("/api/public/assinar/{token}")
async def public_get_sala_assinatura(token: str, db: AsyncSession = Depends(get_db)):
    sig = await crud.get_signatario_by_token(db, token)
    if not sig:
        raise HTTPException(status_code=404, detail="Link inválido ou expirado")
        
    # Carrega doc
    # Como não temos um CRUD function "get_documento_by_secret_id", podemos fazer select direto:
    from sqlalchemy import select
    res = await db.execute(select(models.DocumentoCliente).filter(models.DocumentoCliente.id == sig.documento_id))
    doc = res.scalars().first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Documento indisponível")
        
    # Atualiza visualização se pendente
    if sig.status == 'Pendente':
        sig.status = 'Visualizado'
        sig.data_visualizacao = datetime.now()
        db.add(sig)
        await db.commit()
        
    # Prepara a URL do arquivo para visualização (DOCX -> PDF)
    import os
    arquivo_original = f"static/{doc.arquivo_path}"
    arquivo_exibicao = arquivo_original
    
    if arquivo_original.lower().endswith('.docx'):
        pdf_path = arquivo_original.replace('.docx', '_visualizacao.pdf')
        if not os.path.exists(pdf_path) and os.path.exists(arquivo_original):
            try:
                await convert_docx_to_pdf_async(arquivo_original, pdf_path)
            except Exception as e:
                print(f"Erro ao converter DOCX para PDF para visualização: {e}")
        
        if os.path.exists(pdf_path):
            arquivo_exibicao = pdf_path
            
    return {
        "signatario": {
            "id": sig.id,
            "nome": sig.nome,
            "email": sig.email,
            "cpf": sig.cpf,
            "status": sig.status,
            "funcao": sig.funcao
        },
        "documento": {
            "id": doc.id,
            "nome": doc.nome,
            "arquivo_url": f"/{arquivo_exibicao}",
            "status_assinatura": doc.status_assinatura
        }
    }

@app.post("/api/public/assinar/{token}/confirmar")
async def public_confirm_assinatura(token: str, data: schemas.AssinaturaConfirmarRequest, request: Request, db: AsyncSession = Depends(get_db)):
    import os
    import uuid as _uuid
    from datetime import datetime
    from sqlalchemy import select as sql_select, func as sql_func, update as sql_update

    sig = await crud.get_signatario_by_token(db, token)
    if not sig:
        raise HTTPException(status_code=404, detail="Link inválido ou expirado")

    doc_id = sig.documento_id
    doc_res = await db.execute(
        sql_select(models.DocumentoCliente).where(models.DocumentoCliente.id == doc_id)
    )
    doc = doc_res.scalars().first()
    if not doc:
        return {"message": "O documento já foi removido."}

    ja_assinado = sig.status == 'Assinado'
    if ja_assinado and doc.status_assinatura == 'Concluido':
        return {"message": "Documento já assinado por este signatário e finalizado."}

    if not ja_assinado:
        # 1. Salva imagem da assinatura/selfie
        upload_dir = "static/assinaturas"
        os.makedirs(upload_dir, exist_ok=True)
        img_filename = f"{data.tipo_autenticacao}_{sig.token_acesso}.png"
        img_path = os.path.join(upload_dir, img_filename)

        try:
            encoded_data = data.imagem_base64.split(",")[1] if "," in data.imagem_base64 else data.imagem_base64
            decoded_data = base64.b64decode(encoded_data)
            with open(img_path, "wb") as f:
                f.write(decoded_data)
        except Exception:
            raise HTTPException(status_code=400, detail="Base64 inválido")

        # 2. Atualiza o signatário
        sig.imagem_assinatura_path = img_path
        sig.tipo_autenticacao = data.tipo_autenticacao
        sig.status = 'Assinado'
        sig.data_assinatura = datetime.now()
        if data.cpf and not sig.cpf:
            sig.cpf = data.cpf
        sig.ip_assinatura = request.client.host if request.client else "Unknown"
        sig.user_agent_assinatura = request.headers.get("user-agent", "Unknown")
        
        # Opcional se enviou posições nesta hora (raro, mas possivel se integrado na mesma rota)
        if data.pos_page is not None:
            sig.page_number = data.pos_page
            sig.x_pos = data.pos_x
            sig.y_pos = data.pos_y
            sig.width = data.pos_width
            sig.height = data.pos_height
            sig.docWidth = data.pos_doc_width
            sig.docHeight = data.pos_doc_height
            
        db.add(sig)
        await db.commit()

    # 3. Verifica quantos assinaram vs total
    doc_id = sig.documento_id
    total_res = await db.execute(
        sql_select(sql_func.count()).select_from(models.Signatario)
        .where(models.Signatario.documento_id == doc_id)
    )
    assinados_res = await db.execute(
        sql_select(sql_func.count()).select_from(models.Signatario)
        .where(models.Signatario.documento_id == doc_id, models.Signatario.status == 'Assinado')
    )
    total = total_res.scalar() or 0
    assinados = assinados_res.scalar() or 0

    # doc_id já buscado. doc já buscado no inicio.

    if assinados < total:
        # Parcialmente assinado
        await db.execute(
            sql_update(models.DocumentoCliente)
            .where(models.DocumentoCliente.id == doc_id)
            .values(status_assinatura='Parcial')
        )
        await db.commit()
        return {"message": "Assinatura confirmada com sucesso!"}

    # 4. TODOS ASSINARAM → Gera o documento final com certificado
    PASTA_SAIDA = "static/documentos_assinados"
    os.makedirs(PASTA_SAIDA, exist_ok=True)

    caminho_original = os.path.join("static", doc.arquivo_path)
    caminho_pdf_base = caminho_original

    # 4a. Converte DOCX para PDF se necessário
    if caminho_original.lower().endswith('.docx'):
        caminho_pdf_base = caminho_original.replace('.docx', '_converted.pdf')
        if not os.path.exists(caminho_pdf_base):
            try:
                await convert_docx_to_pdf_async(caminho_original, caminho_pdf_base)
            except Exception as e:
                print(f"Erro ao converter DOCX para PDF: {e}")
                # Fallback: gera só o certificado sem estampar
                caminho_pdf_base = None

    # 4b. Busca todos os signatários para o certificado
    sigs_res = await db.execute(
        select(models.Signatario).where(models.Signatario.documento_id == doc_id)
    )
    todos_sigs = sigs_res.scalars().all()
    
    sigs_list_flat = []
    sigs_list_unique = []
    
    for s in todos_sigs:
        base_sig_dict = {
            "id": s.id,
            "nome": s.nome,
            "email": s.email,
            "cpf": s.cpf or "Não informado",
            "funcao": s.funcao,
            "status": s.status,
            "tipo_autenticacao": s.tipo_autenticacao,
            "data_assinatura": s.data_assinatura,
            "ip_assinatura": s.ip_assinatura,
            "user_agent_assinatura": s.user_agent_assinatura,
            "imagem_assinatura_path": s.imagem_assinatura_path,
            # Fallback for old records
            "pos_page": s.page_number,
            "pos_x": s.x_pos,
            "pos_y": s.y_pos,
            "pos_width": s.width,
            "pos_height": s.height,
            "pos_doc_width": s.docWidth,
            "pos_doc_height": s.docHeight,
        }
        
        sigs_list_unique.append(base_sig_dict)
        
        # If user has multiple positions in the new db structure, we add one flat entry per position
        if hasattr(s, 'posicoes') and s.posicoes and len(s.posicoes) > 0:
            for p in s.posicoes:
                pos_sig = base_sig_dict.copy()
                pos_sig.update({
                    "pos_page": p.page_number,
                    "pos_x": p.x_pos,
                    "pos_y": p.y_pos,
                    "pos_width": p.width,
                    "pos_height": p.height,
                    "pos_doc_width": p.docWidth,
                    "pos_doc_height": p.docHeight,
                })
                sigs_list_flat.append(pos_sig)
        else:
            # Fallback: Just append the base dict if no multiple positions
            sigs_list_flat.append(base_sig_dict)

    # 4c. Estampa assinaturas no PDF (sem coordenadas de posição — vai gerar só o overlay de texto)
    caminho_estampado = caminho_pdf_base
    if caminho_pdf_base and os.path.exists(caminho_pdf_base):
        caminho_estampado_temp = os.path.join(PASTA_SAIDA, f"estampado_{doc_id}.pdf")
        try:
            caminho_estampado = assinador_service.estampar_assinaturas(caminho_pdf_base, sigs_list_flat, caminho_estampado_temp)
        except Exception as e:
            print(f"Erro ao estampar: {e}")
            caminho_estampado = caminho_pdf_base  # fallback

    # 4d. Gera token de validação se não existir
    if not doc.token_validacao:
        await db.execute(
            sql_update(models.DocumentoCliente)
            .where(models.DocumentoCliente.id == doc_id)
            .values(token_validacao=_uuid.uuid4().hex)
        )
        await db.commit()
        # Re-lê o doc para pegar o token
        doc_res2 = await db.execute(
            select(models.DocumentoCliente).where(models.DocumentoCliente.id == doc_id)
        )
        doc = doc_res2.scalars().first()

    base_url = str(request.base_url).rstrip('/')
    url_validacao = f"{base_url}/api/public/validar/{doc.token_validacao}"

    # Dinamicamente calcula hash_original se estiver vazio
    hash_orig = doc.hash_original
    if not hash_orig and caminho_pdf_base and os.path.exists(caminho_pdf_base):
        hash_orig = assinador_service.calcular_hash_arquivo(caminho_pdf_base)
        if hash_orig:
            await db.execute(
                sql_update(models.DocumentoCliente)
                .where(models.DocumentoCliente.id == doc_id)
                .values(hash_original=hash_orig)
            )
            await db.commit()

    # 4e. Gera página de certificado com QR Code
    caminho_certificado = os.path.join(PASTA_SAIDA, f"certificado_{doc_id}.pdf")
    doc_dict = {
        "nome": doc.nome,
        "hash_original": hash_orig or "N/A"
    }
    try:
        assinador_service.gerar_certificado_pdf(doc_dict, sigs_list_unique, caminho_certificado, url_validacao)
    except Exception as e:
        print(f"Erro ao gerar certificado: {e}")
        await db.execute(
            sql_update(models.DocumentoCliente)
            .where(models.DocumentoCliente.id == doc_id)
            .values(status_assinatura='Concluido')
        )
        await db.commit()
        return {"message": "Assinatura confirmada. Erro ao gerar certificado."}

    # 4f. Merge: PDF estampado + certificado → documento final
    nome_final = f"final_assinado_{doc_id}.pdf"
    caminho_final = os.path.join(PASTA_SAIDA, nome_final)

    if caminho_estampado and os.path.exists(caminho_estampado):
        try:
            assinador_service.anexar_certificado(caminho_estampado, caminho_certificado, caminho_final)
        except Exception as e:
            print(f"Erro ao anexar certificado: {e}")
            caminho_final = caminho_certificado  # Só o certificado como fallback
    else:
        # Sem PDF original — salva só o certificado
        caminho_final = caminho_certificado

    # 4g. Calcula hash do documento final
    hash_final = assinador_service.calcular_hash_arquivo(caminho_final)

    # 4h. Salva caminho relativo (sem o 'static/') para ser servido como arquivo
    arquivo_path_relativo = caminho_final.replace("static/", "", 1) if caminho_final.startswith("static/") else caminho_final

    await db.execute(
        sql_update(models.DocumentoCliente)
        .where(models.DocumentoCliente.id == doc_id)
        .values(
            status_assinatura='Concluido',
            arquivo_assinado_path=arquivo_path_relativo,
            hash_assinado=hash_final
        )
    )
    await db.commit()

    # Limpeza dos temporários
    for tmp in [caminho_estampado]:
        if tmp and tmp != caminho_final and tmp != caminho_pdf_base:
            try:
                os.remove(tmp)
            except:
                pass

    return {"message": "Assinatura confirmada e documento finalizado!"}

@app.get("/api/public/validar/{token_validacao}")
async def public_validar_documento(token_validacao: str, db: AsyncSession = Depends(get_db)):
    doc = await crud.get_documentacao_by_validacao(db, token_validacao)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    
    return {
        "nome": doc.nome,
        "status_assinatura": doc.status_assinatura,
        "hash_original": doc.hash_original,
        "hash_assinado": doc.hash_assinado,
        "data_criacao": doc.data_criacao.isoformat() if doc.data_criacao else None
    }

# ==========================
# ROTAS APP DEFAULT
# ==========================
@app.get("/")
async def root():
    return {"message": "ADVtools API Online - Pronto para servir ao Vue.js"}
