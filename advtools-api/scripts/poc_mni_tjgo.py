"""
PoC: Teste REAL do WebService MNI do PROJUDI/TJGO
Usa credenciais do .env (PROJUDI_USER e PROJUDI_PASSWORD)

WSDL: https://projudi.tjgo.jus.br/IntercomunicacaoService?WSDL
MNI Version: 2.2.2
Processo Teste: 5760243-22.2025.8.09.0051
"""

import os
import sys
import base64
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Carrega .env da raiz do projeto
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(env_path)

PROJUDI_USER = os.getenv("PROJUDI_USER", "")
PROJUDI_PASSWORD = os.getenv("PROJUDI_PASSWORD", "")
WSDL_URL = "https://projudi.tjgo.jus.br/IntercomunicacaoService?WSDL"
PROCESSO_TESTE = "57602432220258090051"

if not PROJUDI_USER or not PROJUDI_PASSWORD:
    print("[ERRO] PROJUDI_USER e PROJUDI_PASSWORD nao encontrados no .env")
    sys.exit(1)


def criar_cliente():
    from zeep import Client
    from zeep.settings import Settings
    settings = Settings(strict=False, xml_huge_tree=True)
    print(f"[INFO] Conectando ao WSDL: {WSDL_URL}")
    client = Client(wsdl=WSDL_URL, settings=settings)
    print("[OK] WSDL carregado com sucesso!")
    return client


def testar_consulta_processo(client):
    print("\n" + "=" * 70)
    print("  TESTE 1: consultarProcesso (SEM documentos)")
    print("=" * 70)
    print(f"  Usuario: {PROJUDI_USER[:6]}***")
    print(f"  Processo: {PROCESSO_TESTE}")

    try:
        response = client.service.consultarProcesso(
            idConsultante=PROJUDI_USER,
            senhaConsultante=PROJUDI_PASSWORD,
            numeroProcesso=PROCESSO_TESTE,
            movimentos=True,
            incluirCabecalho=True,
            incluirDocumentos=False
        )

        print(f"\n  sucesso: {response.sucesso}")
        print(f"  mensagem: {response.mensagem}")

        if not response.sucesso:
            print("\n  [FALHA] Autenticacao ou processo nao encontrado.")
            return False

        proc = response.processo
        if not proc:
            print("  [FALHA] Resposta sucesso=true mas sem dados de processo.")
            return False

        # -- Cabecalho --
        print("\n  --- CABECALHO DO PROCESSO ---")
        dados = proc.dadosBasicos
        if dados:
            print(f"  Numero: {getattr(dados, 'numero', 'N/A')}")
            print(f"  Classe Processual (cod): {getattr(dados, 'classeProcessual', 'N/A')}")
            print(f"  Localidade: {getattr(dados, 'codigoLocalidade', 'N/A')}")
            print(f"  Nivel Sigilo: {getattr(dados, 'nivelSigilo', 'N/A')}")
            print(f"  Data Ajuizamento: {getattr(dados, 'dataAjuizamento', 'N/A')}")
            print(f"  Valor Causa: {getattr(dados, 'valorCausa', 'N/A')}")

            # Orgao Julgador
            orgao = getattr(dados, 'orgaoJulgador', None)
            if orgao:
                print(f"  Orgao Julgador: {getattr(orgao, 'nomeOrgao', 'N/A')} (cod: {getattr(orgao, 'codigoOrgao', '')})")
                print(f"  Instancia: {getattr(orgao, 'instancia', 'N/A')}")

            # Polos
            polos = getattr(dados, 'polo', [])
            if polos:
                print(f"\n  --- POLOS PROCESSUAIS ({len(polos)} polos) ---")
                for polo in polos:
                    tipo_polo = getattr(polo, 'polo', '??')
                    partes = getattr(polo, 'parte', [])
                    print(f"    Polo {tipo_polo}: {len(partes)} parte(s)")
                    for parte in partes:
                        pessoa = getattr(parte, 'pessoa', None)
                        if pessoa:
                            print(f"      - {getattr(pessoa, 'nome', 'N/A')} ({getattr(pessoa, 'tipoPessoa', '')})")
                            doc_principal = getattr(pessoa, 'numeroDocumentoPrincipal', None)
                            if doc_principal:
                                print(f"        Doc: {doc_principal}")
                        # Advogados
                        advs = getattr(parte, 'advogado', [])
                        for adv in (advs or []):
                            print(f"        Adv: {getattr(adv, 'nome', 'N/A')} - OAB: {getattr(adv, 'inscricao', 'N/A')}")

            # Assuntos
            assuntos = getattr(dados, 'assunto', [])
            if assuntos:
                print(f"\n  --- ASSUNTOS ({len(assuntos)}) ---")
                for ass in assuntos:
                    cod = getattr(ass, 'codigoNacional', None)
                    principal = getattr(ass, 'principal', False)
                    local = getattr(ass, 'assuntoLocal', None)
                    desc_local = getattr(local, 'descricao', '') if local else ''
                    tag = " [PRINCIPAL]" if principal else ""
                    print(f"    - Cod Nacional: {cod}{tag} {desc_local}")

        # -- Movimentacoes --
        movs = getattr(proc, 'movimento', []) or []
        print(f"\n  --- MOVIMENTACOES ({len(movs)} total) ---")
        for i, mov in enumerate(movs[:10]):
            dt = getattr(mov, 'dataHora', 'N/A')
            id_mov = getattr(mov, 'identificadorMovimento', '')
            sigilo = getattr(mov, 'nivelSigilo', 0)

            # Movimento nacional
            mov_nac = getattr(mov, 'movimentoNacional', None)
            cod_nac = getattr(mov_nac, 'codigoNacional', '') if mov_nac else ''
            comps_nac = getattr(mov_nac, 'complemento', []) if mov_nac else []

            # Movimento local
            mov_loc = getattr(mov, 'movimentoLocal', None)
            desc_loc = getattr(mov_loc, 'descricao', '') if mov_loc else ''
            cod_loc = getattr(mov_loc, 'codigoMovimento', '') if mov_loc else ''

            # Complementos do movimento
            comps = getattr(mov, 'complemento', []) or []

            # Documentos vinculados
            docs_vinc = getattr(mov, 'idDocumentoVinculado', []) or []

            print(f"    [{i+1:>3}] {dt}")
            if cod_nac:
                print(f"          Nacional: cod={cod_nac}")
                if comps_nac:
                    for c in comps_nac[:3]:
                        print(f"            Complemento: {c}")
            if desc_loc:
                print(f"          Local: {desc_loc} (cod={cod_loc})")
            if comps:
                for c in comps[:3]:
                    print(f"          Comp: {c}")
            if docs_vinc:
                print(f"          Docs vinculados: {docs_vinc}")

        if len(movs) > 10:
            print(f"    ... e mais {len(movs) - 10} movimentacoes")

        # -- Documentos (metadata only, sem conteudo) --
        docs = getattr(proc, 'documento', []) or []
        print(f"\n  --- DOCUMENTOS LISTADOS ({len(docs)}) ---")
        for i, doc in enumerate(docs[:10]):
            id_doc = getattr(doc, 'idDocumento', 'N/A')
            tipo = getattr(doc, 'tipoDocumento', 'N/A')
            mime = getattr(doc, 'mimetype', 'N/A')
            desc = getattr(doc, 'descricao', '')
            dt_doc = getattr(doc, 'dataHora', '')
            has_content = getattr(doc, 'conteudo', None) is not None
            movimento_ref = getattr(doc, 'movimento', '')
            print(f"    [{i+1:>3}] ID={id_doc} | Tipo={tipo} | MIME={mime} | Mov={movimento_ref}")
            if desc:
                print(f"          Descricao: {desc}")
            print(f"          Data: {dt_doc} | Conteudo presente: {'SIM' if has_content else 'NAO (incluirDocumentos=false)'}")

        if len(docs) > 10:
            print(f"    ... e mais {len(docs) - 10} documentos")

        return True

    except Exception as e:
        print(f"  [ERRO] {type(e).__name__}: {e}")
        return False


def testar_consulta_com_documentos(client):
    """Se o teste anterior passou, agora pede COM documentos para ver o inteiro teor."""
    print("\n" + "=" * 70)
    print("  TESTE 2: consultarProcesso (COM documentos / inteiro teor)")
    print("=" * 70)

    try:
        response = client.service.consultarProcesso(
            idConsultante=PROJUDI_USER,
            senhaConsultante=PROJUDI_PASSWORD,
            numeroProcesso=PROCESSO_TESTE,
            movimentos=True,
            incluirCabecalho=True,
            incluirDocumentos=True
        )

        print(f"\n  sucesso: {response.sucesso}")
        print(f"  mensagem: {response.mensagem}")

        if not response.sucesso:
            print("  [INFO] Pode ser que incluirDocumentos=true nao seja permitido para este processo.")
            return

        proc = response.processo
        docs = getattr(proc, 'documento', []) or []
        print(f"\n  Documentos retornados: {len(docs)}")

        output_dir = Path(__file__).parent / "poc_output"
        output_dir.mkdir(exist_ok=True)

        for i, doc in enumerate(docs[:5]):
            id_doc = getattr(doc, 'idDocumento', f'doc_{i}')
            tipo = getattr(doc, 'tipoDocumento', 'N/A')
            mime = getattr(doc, 'mimetype', 'application/octet-stream')
            desc = getattr(doc, 'descricao', '')
            conteudo = getattr(doc, 'conteudo', None)

            print(f"\n    Doc [{i+1}] ID={id_doc}")
            print(f"      Tipo: {tipo} | MIME: {mime}")
            print(f"      Descricao: {desc}")

            if conteudo is not None:
                # conteudo pode ser bytes (base64 ja decodificado pelo zeep) ou raw
                if isinstance(conteudo, bytes):
                    size_kb = len(conteudo) / 1024
                    print(f"      Conteudo: {size_kb:.1f} KB")

                    # Determinar extensao
                    ext = ".pdf"
                    if mime and "html" in mime:
                        ext = ".html"
                    elif mime and "text" in mime:
                        ext = ".txt"

                    filename = f"doc_{id_doc}{ext}"
                    filepath = output_dir / filename
                    with open(filepath, "wb") as f:
                        f.write(conteudo)
                    print(f"      SALVO em: {filepath}")
                else:
                    # Pode ser string base64
                    print(f"      Conteudo tipo: {type(conteudo).__name__}, len={len(str(conteudo))}")
                    try:
                        decoded = base64.b64decode(str(conteudo))
                        size_kb = len(decoded) / 1024
                        print(f"      Decodificado: {size_kb:.1f} KB")
                        filename = f"doc_{id_doc}.pdf"
                        filepath = output_dir / filename
                        with open(filepath, "wb") as f:
                            f.write(decoded)
                        print(f"      SALVO em: {filepath}")
                    except Exception as e2:
                        print(f"      [AVISO] Nao foi possivel decodificar: {e2}")
            else:
                print(f"      Conteudo: VAZIO (documento pode estar sob sigilo ou nao disponivel)")

        if len(docs) > 5:
            print(f"\n    ... {len(docs) - 5} documentos adicionais nao foram salvos neste teste")

    except Exception as e:
        print(f"  [ERRO] {type(e).__name__}: {e}")


def testar_avisos_pendentes(client):
    print("\n" + "=" * 70)
    print("  TESTE 3: consultarAvisosPendentes (intimacoes)")
    print("=" * 70)

    try:
        response = client.service.consultarAvisosPendentes(
            idConsultante=PROJUDI_USER,
            senhaConsultante=PROJUDI_PASSWORD,
            idRepresentado=PROJUDI_USER
        )

        print(f"\n  sucesso: {response.sucesso}")
        print(f"  mensagem: {response.mensagem}")

        avisos = getattr(response, 'aviso', []) or []
        if avisos:
            print(f"\n  Avisos Pendentes: {len(avisos)}")
            for i, aviso in enumerate(avisos[:10]):
                id_aviso = getattr(aviso, 'idAviso', 'N/A')
                tipo_com = getattr(aviso, 'tipoComunicacao', 'N/A')
                data_disp = getattr(aviso, 'dataDisponibilizacao', 'N/A')

                proc_aviso = getattr(aviso, 'processo', None)
                num_proc = getattr(proc_aviso, 'numero', 'N/A') if proc_aviso else 'N/A'

                dest = getattr(aviso, 'destinatario', None)
                dest_pessoa = getattr(dest, 'pessoa', None) if dest else None
                dest_nome = getattr(dest_pessoa, 'nome', 'N/A') if dest_pessoa else 'N/A'

                print(f"    [{i+1}] ID={id_aviso} | Tipo={tipo_com}")
                print(f"         Processo: {num_proc}")
                print(f"         Destinatario: {dest_nome}")
                print(f"         Data: {data_disp}")
        else:
            print("  Nenhum aviso pendente encontrado.")

    except Exception as e:
        print(f"  [ERRO] {type(e).__name__}: {e}")


def testar_alteracao(client):
    print("\n" + "=" * 70)
    print("  TESTE 4: consultarAlteracao (monitoramento por hash)")
    print("=" * 70)

    try:
        response = client.service.consultarAlteracao(
            idConsultante=PROJUDI_USER,
            senhaConsultante=PROJUDI_PASSWORD,
            numeroProcesso=PROCESSO_TESTE
        )

        print(f"\n  sucesso: {response.sucesso}")
        print(f"  mensagem: {response.mensagem}")

        if response.sucesso:
            h_cab = getattr(response, 'hashCabecalho', None)
            h_mov = getattr(response, 'hashMovimentacoes', None)
            h_doc = getattr(response, 'hashDocumentos', None)
            print(f"  Hash Cabecalho: {h_cab}")
            print(f"  Hash Movimentacoes: {h_mov}")
            print(f"  Hash Documentos: {h_doc}")

    except Exception as e:
        print(f"  [ERRO] {type(e).__name__}: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  PoC MNI WebService PROJUDI/TJGO - TESTE COM CREDENCIAIS REAIS")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)

    client = criar_cliente()

    # Teste 1: Consulta sem documentos (leve)
    sucesso = testar_consulta_processo(client)

    if sucesso:
        # Teste 2: Consulta COM documentos (inteiro teor)
        testar_consulta_com_documentos(client)

    # Teste 3: Avisos pendentes
    testar_avisos_pendentes(client)

    # Teste 4: Monitoramento por hash
    testar_alteracao(client)

    print("\n" + "=" * 70)
    print("  FIM DOS TESTES")
    print("=" * 70)
