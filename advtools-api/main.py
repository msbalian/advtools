import os
import logging
import traceback
import mimetypes
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Registrar MIME types para evitar problemas em ambientes Linux (como o Docker slim)
mimetypes.add_type('application/vnd.openxmlformats-officedocument.wordprocessingml.document', '.docx')
mimetypes.add_type('application/pdf', '.pdf')
mimetypes.add_type('image/jpeg', '.jpg')
mimetypes.add_type('image/jpeg', '.jpeg')
mimetypes.add_type('image/png', '.png')

# Configura log para arquivo para vermos erros 500 que uvicorn esconde
logging.basicConfig(filename='api_errors.log', level=logging.ERROR)

# Este app é sua API core em FastAPI
from config import Config
from init_db import init_default_data
from services.storage_audit_service import run_storage_audit

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialização (on startup)
    try:
        await init_default_data()
        # Auditoria de armazenamento para garantir integridade no startup
        await run_storage_audit(fix=True)
    except Exception as e:
        print(f"Erro na inicialização de dados: {e}")
    yield

app = FastAPI(title="ADVtools API", lifespan=lifespan)

# Setup CORS
origins = [o.strip() for o in Config.CORS_ORIGINS.split(",")]

# Servir arquivos da pasta static (como as logomarcas) de forma absoluta
static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(static_path, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_path), name="static")

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
from routers import (
    auth, usuarios, escritorios, clientes, servicos, 
    partes, processos, financeiro, tarefas, 
    documentos, pastas, assinaturas, superadmin, configuracoes, arquivos
)

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(escritorios.router)
app.include_router(escritorios.router_singular)
app.include_router(clientes.router)
app.include_router(servicos.router)
app.include_router(partes.router)
app.include_router(partes.router_clientes_partes)
app.include_router(processos.router)
app.include_router(financeiro.router)
app.include_router(tarefas.router)
app.include_router(pastas.router)
app.include_router(documentos.router_modelos)
app.include_router(documentos.router_documentos)
app.include_router(documentos.router_clientes_docs)
app.include_router(documentos.router_redator)
app.include_router(assinaturas.router_assinaturas)
app.include_router(assinaturas.router_assinativas_public)
app.include_router(superadmin.router)
app.include_router(configuracoes.router)
app.include_router(arquivos.router)

# Finalizado setup de rotas

# ==========================
# ROTAS APP DEFAULT
# ==========================
@app.get("/")
async def root():
    return {"message": "ADVtools API Online - Pronto para servir ao Vue.js"}
