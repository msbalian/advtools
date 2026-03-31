import os
import logging
import traceback
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Configura log para arquivo para vermos erros 500 que uvicorn esconde
logging.basicConfig(filename='api_errors.log', level=logging.ERROR)

# Este app é sua API core em FastAPI
from config import Config
from init_db import init_default_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialização (on startup)
    try:
        await init_default_data()
    except Exception as e:
        print(f"Erro na inicialização de dados: {e}")
    yield

app = FastAPI(title="ADVtools API", lifespan=lifespan)

# Setup CORS
cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost,http://localhost:5173,http://localhost:5174")
origins = [o.strip() for o in cors_origins_str.split(",")]

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
