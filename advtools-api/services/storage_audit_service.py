import os
import shutil
import asyncio
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import models
from database import AsyncSessionLocal

# Configurações de diretórios (Caminhos relativos ao diretório do app)
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(APP_DIR, "static")
STORAGE_DIR = os.path.join(STATIC_DIR, "armazenamento")

# Pastas legado que devem ser limpas se não houver registros no banco
LEGACY_STATIC_DIRS = [
    os.path.join(STATIC_DIR, "logos"),
    os.path.join(STATIC_DIR, "modelos"),
    os.path.join(STATIC_DIR, "assinaturas") # Caso exista fora de armazenamento
]

async def run_storage_audit(fix=True):
    """
    Executa a auditoria e migração de isolamento por escritório.
    Garante integridade entre Banco e Disco no startup.
    """
    if not os.path.exists(STATIC_DIR):
        return

    print(f"--- [STARTUP] Auditoria de Armazenamento Automática ---")
    
    async with AsyncSessionLocal() as db:
        try:
            # 1. Carregar registros
            res_modelos = await db.execute(select(models.ModeloDocumento))
            modelos = res_modelos.scalars().all()
            
            res_docs = await db.execute(select(models.DocumentoCliente))
            docs = res_docs.scalars().all()
            
            res_escritorios = await db.execute(select(models.Escritorio))
            escritorios = res_escritorios.scalars().all()
            
            res_sigs = await db.execute(select(models.Signatario).options(selectinload(models.Signatario.documento)))
            signatarios = res_sigs.scalars().all()
            
            # Conjunto de IDs de escritórios válidos para segurança na limpeza de pastas
            valid_office_ids = {esc.id for esc in escritorios}
            query_success = len(escritorios) > 0 # Pelo menos um escritório (o Master) deve existir
            
            db_files = [] 
            migrations_count = 0

            # --- PROCESSAR MODELOS ---
            for m in modelos:
                old_path = m.arquivo_path
                new_rel_dir = f"armazenamento/escritorio_{m.escritorio_id}/modelos"
                expected_path = os.path.join(new_rel_dir, os.path.basename(old_path)).replace("\\", "/")
                
                if old_path != expected_path:
                    if await _migrate_file(db, m, "arquivo_path", old_path, expected_path, fix):
                        migrations_count += 1
                        db_files.append(expected_path)
                    else:
                        db_files.append(old_path)
                else:
                    db_files.append(old_path)

            # --- PROCESSAR DOCUMENTOS ---
            for d in docs:
                # Caminho Original
                old_path = d.arquivo_path
                filename = os.path.basename(old_path)
                
                if d.cliente_id:
                    new_rel_dir = f"armazenamento/escritorio_{d.escritorio_id}/clientes/cliente_{d.cliente_id}/documentos"
                else:
                    new_rel_dir = f"armazenamento/escritorio_{d.escritorio_id}/internos/documentos"
                    
                expected_path = os.path.join(new_rel_dir, filename).replace("\\", "/")
                
                if old_path != expected_path:
                    if await _migrate_file(db, d, "arquivo_path", old_path, expected_path, fix):
                        migrations_count += 1
                        db_files.append(expected_path)
                    else:
                        db_files.append(old_path)
                else:
                    db_files.append(old_path)
                
                # Documento Assinado (PDF Final)
                if d.arquivo_assinado_path:
                    old_sig_path = d.arquivo_assinado_path
                    if d.cliente_id:
                        new_sig_dir = f"armazenamento/escritorio_{d.escritorio_id}/clientes/cliente_{d.cliente_id}/assinados"
                    else:
                        new_sig_dir = f"armazenamento/escritorio_{d.escritorio_id}/internos/assinados"
                    
                    expected_sig_path = os.path.join(new_sig_dir, os.path.basename(old_sig_path)).replace("\\", "/")
                    if old_sig_path != expected_sig_path:
                        if await _migrate_file(db, d, "arquivo_assinado_path", old_sig_path, expected_sig_path, fix):
                            migrations_count += 1
                            db_files.append(expected_sig_path)
                        else:
                            db_files.append(old_sig_path)
                    else:
                        db_files.append(old_sig_path)

            # --- PROCESSAR LOGOMARCAS ---
            for esc in escritorios:
                if not esc.logo_path: continue
                
                old_path = esc.logo_path
                new_rel_dir = f"armazenamento/escritorio_{esc.id}/logos"
                expected_path = os.path.join(new_rel_dir, os.path.basename(old_path)).replace("\\", "/")
                
                if old_path != expected_path:
                    if await _migrate_file(db, esc, "logo_path", old_path, expected_path, fix):
                        migrations_count += 1
                        db_files.append(expected_path)
                    else:
                        db_files.append(old_path)
                else:
                    db_files.append(old_path)

            # --- PROCESSAR IMAGENS DE ASSINATURA ---
            for s in signatarios:
                if not s.imagem_assinatura_path: continue
                old_path = s.imagem_assinatura_path
                esc_id = s.documento.escritorio_id if s.documento else 1
                new_rel_dir = f"armazenamento/escritorio_{esc_id}/assinaturas"
                expected_path = os.path.join(new_rel_dir, os.path.basename(old_path)).replace("\\", "/")
                if old_path != expected_path:
                    if await _migrate_file(db, s, "imagem_assinatura_path", old_path, expected_path, fix):
                        migrations_count += 1
                        db_files.append(expected_path)
                    else:
                        db_files.append(old_path)
                else:
                    db_files.append(old_path)

            if fix and migrations_count > 0:
                await db.commit()
                print(f"✅ {migrations_count} registros de arquivos migrados para nova estrutura.")

            # --- IDENTIFICAR E LIMPAR ÓRFÃOS ---
            if fix:
                orphans_deleted = 0
                dirs_to_sweep = [STORAGE_DIR] + [d for d in LEGACY_STATIC_DIRS if os.path.exists(d)]
                
                for sweep_dir in dirs_to_sweep:
                    for root, dirs_file, files in os.walk(sweep_dir):
                        for file in files:
                            abs_path = os.path.join(root, file)
                            rel_path = os.path.relpath(abs_path, STATIC_DIR).replace("\\", "/")
                            
                            if rel_path not in db_files:
                                try:
                                    os.remove(abs_path)
                                    orphans_deleted += 1
                                except:
                                    pass
                if orphans_deleted > 0:
                    print(f"Sweep: {orphans_deleted} arquivos órfãos removidos.")

                # --- LIMPAR DIRETÓRIOS VAZIOS ---
                for sweep_dir in dirs_to_sweep:
                    # Incluímos o próprio sweep_dir na lista de monitoramento de remoção
                    for root, dirs, files in os.walk(sweep_dir, topdown=False):
                        for name in dirs:
                            dir_path = os.path.join(root, name)
                            
                            # Logica para pastas de escritórios
                            if name.startswith("escritorio_"):
                                try:
                                    off_id = int(name.replace("escritorio_", ""))
                                    # SÓ exclui se tivermos certeza que o ID não existe E a query de escritórios funcionou
                                    if query_success and off_id not in valid_office_ids:
                                        print(f"Limpeza: Removendo pasta de escritório inexistente: {name}")
                                        shutil.rmtree(dir_path, ignore_errors=True)
                                        continue
                                    else:
                                        # Escritório ativo ou falha na query, mantém a pasta
                                        continue
                                except:
                                    continue

                            if not os.path.exists(dir_path): continue
                            if not os.listdir(dir_path):
                                try:
                                    os.rmdir(dir_path)
                                except:
                                    pass
                    
                    # Checagem final do sweep_dir em si (após limpar subpastas)
                    if sweep_dir != STORAGE_DIR and os.path.exists(sweep_dir) and not os.listdir(sweep_dir):
                        try:
                            os.rmdir(sweep_dir)
                            print(f"Limpeza: Diretório legado removido: {sweep_dir}")
                        except:
                            pass

        except Exception as e:
            print(f"⚠️ Falha na auditoria de armazenamento: {e}")
            await db.rollback()

    print(f"--- Auditoria Finalizada ---")

async def _migrate_file(db: AsyncSession, obj, attr_name, old_rel_path, new_rel_path, fix):
    old_abs = _find_physical_file(old_rel_path)
    new_abs = os.path.join(STATIC_DIR, new_rel_path)
    
    if not old_abs:
        return False

    if fix:
        os.makedirs(os.path.dirname(new_abs), exist_ok=True)
        if os.path.abspath(old_abs) != os.path.abspath(new_abs):
            shutil.move(old_abs, new_abs)
        setattr(obj, attr_name, new_rel_path)
        db.add(obj)
        return True
    return False

def _find_physical_file(rel_path):
    path1 = os.path.join(STATIC_DIR, rel_path)
    if os.path.exists(path1): return path1
    
    filename = os.path.basename(rel_path)
    legacy_spots = ["modelos", "logos", "assinaturas"]
    for spot in legacy_spots:
        p = os.path.join(STATIC_DIR, spot, filename)
        if os.path.exists(p): return p
        p2 = os.path.join(STORAGE_DIR, spot, filename)
        if os.path.exists(p2): return p2
        
    path_root_storage = os.path.join(STORAGE_DIR, rel_path.replace("armazenamento/", "", 1) if rel_path.startswith("armazenamento/") else rel_path)
    if os.path.exists(path_root_storage): return path_root_storage
    
    for root, dirs, files in os.walk(STORAGE_DIR):
        if filename in files:
            return os.path.join(root, filename)
            
    return None
