import os
import logging
import traceback

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Configura log para arquivo para vermos erros 500 que uvicorn esconde
logging.basicConfig(filename='api_errors.log', level=logging.ERROR)

# Este app é sua API core em FastAPI
from config import Config

app = FastAPI(title="ADVtools API")

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
from routers import auth as auth_router

app.include_router(auth_router.router)

from routers import usuarios as usuarios_router
from routers import escritorios as escritorios_router

app.include_router(usuarios_router.router)
app.include_router(escritorios_router.router)
app.include_router(escritorios_router.router_singular)

from routers import clientes as clientes_router
from routers import servicos as servicos_router
from routers import partes as partes_router

app.include_router(clientes_router.router)
app.include_router(servicos_router.router)
app.include_router(partes_router.router)
app.include_router(partes_router.router_clientes_partes)

# ==========================
# ROTAS DE MODELOS
# ==========================

from routers import documentos as documentos_router
from routers import pastas as pastas_router

app.include_router(pastas_router.router)
app.include_router(documentos_router.router_modelos)
app.include_router(documentos_router.router_documentos)
app.include_router(documentos_router.router_clientes_docs)
app.include_router(documentos_router.router_redator)

from routers import assinaturas as assinaturas_router

app.include_router(assinaturas_router.router_assinaturas)
app.include_router(assinaturas_router.router_assinativas_public)
from routers import superadmin as superadmin_router
app.include_router(superadmin_router.router)

# ==========================
# ROTAS APP DEFAULT
# ==========================
@app.get("/")
async def root():
    return {"message": "ADVtools API Online - Pronto para servir ao Vue.js"}
