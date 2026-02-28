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
from services.documento_service import convert_docx_to_pdf_async

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

from services.auth_service import get_current_user, oauth2_scheme
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

app.include_router(documentos_router.router_modelos)
app.include_router(documentos_router.router_documentos)
app.include_router(documentos_router.router_clientes_docs)
app.include_router(documentos_router.router_redator)

from routers import assinaturas as assinaturas_router

app.include_router(assinaturas_router.router_assinaturas)
app.include_router(assinaturas_router.router_assinativas_public)

# ==========================
# ROTAS APP DEFAULT
# ==========================
@app.get("/")
async def root():
    return {"message": "ADVtools API Online - Pronto para servir ao Vue.js"}
