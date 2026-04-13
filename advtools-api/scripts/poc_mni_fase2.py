"""
PoC Fase 2: Tentar recuperar o CONTEUDO dos documentos do PROJUDI/TJGO
Testa varias estrategias para obter o inteiro teor.
"""

import os
import sys
import base64
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(env_path)

PROJUDI_USER = os.getenv("PROJUDI_USER", "")
PROJUDI_PASSWORD = os.getenv("PROJUDI_PASSWORD", "")
WSDL_URL = "https://projudi.tjgo.jus.br/IntercomunicacaoService?WSDL"
PROCESSO_TESTE = "57602432220258090051"

# IDs de documentos descobertos no teste anterior
DOC_SENTENCA = "516529955"      # Sentenca (text/html)
DOC_CERTIDAO = "516323305"      # Certidao (text/html)
DOC_PETICAO = "515391818"       # Peticao (application/pdf)

OUTPUT_DIR = Path(__file__).parent / "poc_output"
OUTPUT_DIR.mkdir(exist_ok=True)


def criar_cliente():
    from zeep import Client
    from zeep.settings import Settings
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, settings=settings)
    print("[OK] Cliente SOAP criado")
    return client


def salvar_documento(doc, label=""):
    """Salva um documento retornado pelo MNI."""
    id_doc = getattr(doc, 'idDocumento', 'unknown')
    tipo = getattr(doc, 'tipoDocumento', 'N/A')
    mime = getattr(doc, 'mimetype', '')
    desc = getattr(doc, 'descricao', '')
    conteudo = getattr(doc, 'conteudo', None)
    dt = getattr(doc, 'dataHora', '')

    print(f"    ID={id_doc} | Tipo={tipo} | MIME={mime}")
    print(f"    Descricao: {desc}")
    print(f"    Data: {dt}")

    if conteudo is not None:
        if isinstance(conteudo, bytes):
            size_kb = len(conteudo) / 1024
            print(f"    >>> CONTEUDO PRESENTE: {size_kb:.1f} KB")
            ext = ".html" if mime and "html" in mime else ".pdf"
            filename = f"{label}_{id_doc}{ext}"
            filepath = OUTPUT_DIR / filename
            with open(filepath, "wb") as f:
                f.write(conteudo)
            print(f"    >>> SALVO: {filepath}")

            # Preview do conteudo HTML
            if "html" in (mime or ""):
                preview = conteudo.decode("utf-8", errors="replace")[:500]
                print(f"    >>> PREVIEW:\n    {preview[:400]}...")
            return True
        elif isinstance(conteudo, str):
            print(f"    >>> Conteudo como string, len={len(conteudo)}")
            try:
                decoded = base64.b64decode(conteudo)
                size_kb = len(decoded) / 1024
                print(f"    >>> Decodificado base64: {size_kb:.1f} KB")
                ext = ".html" if mime and "html" in mime else ".pdf"
                filepath = OUTPUT_DIR / f"{label}_{id_doc}{ext}"
                with open(filepath, "wb") as f:
                    f.write(decoded)
                print(f"    >>> SALVO: {filepath}")
                return True
            except Exception:
                print(f"    >>> Conteudo nao e base64. Primeiros 200 chars: {conteudo[:200]}")
                filepath = OUTPUT_DIR / f"{label}_{id_doc}.txt"
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(conteudo)
                print(f"    >>> SALVO como texto: {filepath}")
                return True
    else:
        print(f"    >>> CONTEUDO VAZIO")
        return False


# ──────────────────────────────────────────────
# ESTRATEGIA 1: Pedir documento especifico via parametro documento[]
# ──────────────────────────────────────────────

def estrategia_1_documento_especifico(client):
    print("\n" + "=" * 70)
    print("  ESTRATEGIA 1: consultarProcesso com documento[] especifico")
    print("  Passando IDs individuais no parametro 'documento'")
    print("=" * 70)

    doc_ids = [DOC_SENTENCA, DOC_CERTIDAO, DOC_PETICAO]
    print(f"  Pedindo documentos: {doc_ids}")

    try:
        response = client.service.consultarProcesso(
            idConsultante=PROJUDI_USER,
            senhaConsultante=PROJUDI_PASSWORD,
            numeroProcesso=PROCESSO_TESTE,
            movimentos=False,
            incluirCabecalho=False,
            incluirDocumentos=True,
            documento=doc_ids
        )

        print(f"\n  sucesso: {response.sucesso}")
        print(f"  mensagem: {response.mensagem}")

        if not response.sucesso:
            print("  [FALHA]")
            return False

        proc = response.processo
        docs = getattr(proc, 'documento', []) or []
        print(f"  Documentos retornados: {len(docs)}")

        any_content = False
        for i, doc in enumerate(docs):
            print(f"\n  Doc [{i+1}]:")
            if salvar_documento(doc, label="e1"):
                any_content = True

        return any_content

    except Exception as e:
        print(f"  [ERRO] {type(e).__name__}: {e}")
        return False


# ──────────────────────────────────────────────
# ESTRATEGIA 2: Pedir apenas 1 documento por vez
# ──────────────────────────────────────────────

def estrategia_2_um_por_vez(client):
    print("\n" + "=" * 70)
    print("  ESTRATEGIA 2: consultarProcesso com 1 documento por vez")
    print("=" * 70)

    for doc_id, nome in [(DOC_SENTENCA, "Sentenca"), (DOC_PETICAO, "Peticao")]:
        print(f"\n  --- Pedindo: {nome} (ID={doc_id}) ---")
        try:
            response = client.service.consultarProcesso(
                idConsultante=PROJUDI_USER,
                senhaConsultante=PROJUDI_PASSWORD,
                numeroProcesso=PROCESSO_TESTE,
                movimentos=False,
                incluirCabecalho=False,
                incluirDocumentos=True,
                documento=[doc_id]
            )

            print(f"  sucesso: {response.sucesso}")
            print(f"  mensagem: {response.mensagem}")

            if response.sucesso and response.processo:
                docs = getattr(response.processo, 'documento', []) or []
                print(f"  Docs retornados: {len(docs)}")
                for doc in docs:
                    salvar_documento(doc, label=f"e2_{nome}")
            else:
                print(f"  [FALHA] Sem dados")

        except Exception as e:
            print(f"  [ERRO] {type(e).__name__}: {e}")


# ──────────────────────────────────────────────
# ESTRATEGIA 3: incluirDocumentos=true sem filtro documento[]
# mas inspecionando o XML raw
# ──────────────────────────────────────────────

def estrategia_3_raw_xml(client):
    print("\n" + "=" * 70)
    print("  ESTRATEGIA 3: Inspecionar resposta XML bruta")
    print("  Verificando se o conteudo vem mas o zeep nao parseia")
    print("=" * 70)

    from zeep.plugins import HistoryPlugin

    history = HistoryPlugin()

    from zeep import Client
    from zeep.settings import Settings
    settings = Settings(strict=False, xml_huge_tree=True, raw_response=False)
    client_debug = Client(wsdl=WSDL_URL, settings=settings, plugins=[history])

    try:
        response = client_debug.service.consultarProcesso(
            idConsultante=PROJUDI_USER,
            senhaConsultante=PROJUDI_PASSWORD,
            numeroProcesso=PROCESSO_TESTE,
            movimentos=False,
            incluirCabecalho=False,
            incluirDocumentos=True,
            documento=[DOC_SENTENCA]
        )

        print(f"  sucesso: {response.sucesso}")

        # Inspecionar XML da resposta
        from lxml import etree
        last_response = history.last_received
        if last_response and 'envelope' in last_response:
            xml_str = etree.tostring(last_response['envelope'], pretty_print=True, encoding='unicode')
            # Procurar por "conteudo" no XML
            if "conteudo" in xml_str.lower():
                # Salvar XML para inspe
                xml_path = OUTPUT_DIR / "response_raw.xml"
                with open(xml_path, "w", encoding="utf-8") as f:
                    f.write(xml_str)
                print(f"  [INFO] XML salvo em: {xml_path}")

                # Verificar se ha conteudo inline
                idx = xml_str.lower().find("conteudo")
                snippet = xml_str[max(0, idx-50):idx+200]
                print(f"  [INFO] Snippet 'conteudo':\n    {snippet[:300]}")
            else:
                print("  [INFO] Tag 'conteudo' NAO encontrada no XML de resposta")
                # Salvar mesmo assim para analise
                xml_path = OUTPUT_DIR / "response_raw.xml"
                with open(xml_path, "w", encoding="utf-8") as f:
                    f.write(xml_str[:5000])
                print(f"  [INFO] Primeiros 5000 chars do XML salvos em: {xml_path}")

            # Verificar tamanho total do XML
            print(f"  [INFO] Tamanho total do XML de resposta: {len(xml_str)} chars")

    except Exception as e:
        print(f"  [ERRO] {type(e).__name__}: {e}")


# ──────────────────────────────────────────────
# ESTRATEGIA 4: consultarTeorComunicacao
# Tenta usar a operacao especifica para inteiro teor
# ──────────────────────────────────────────────

def estrategia_4_teor_comunicacao(client):
    print("\n" + "=" * 70)
    print("  ESTRATEGIA 4: consultarTeorComunicacao")
    print("  Usando um aviso pendente real para testar")
    print("=" * 70)

    # Avisos reais encontrados no teste anterior
    avisos_teste = [
        ("5826704-10.2024.8.09.0051", "410991739"),  # Mais recente (2024)
        ("5248301-94.2018.8.09.0051", "69152137"),
    ]

    for num_proc, id_aviso in avisos_teste:
        proc_limpo = num_proc.replace(".", "").replace("-", "")
        print(f"\n  --- Processo: {num_proc}, Aviso: {id_aviso} ---")
        try:
            response = client.service.consultarTeorComunicacao(
                idConsultante=PROJUDI_USER,
                senhaConsultante=PROJUDI_PASSWORD,
                numeroProcesso=proc_limpo,
                identificadorAviso=id_aviso
            )

            print(f"  sucesso: {response.sucesso}")
            print(f"  mensagem: {response.mensagem}")

            comunicacoes = getattr(response, 'comunicacao', []) or []
            if comunicacoes:
                print(f"  Comunicacoes retornadas: {len(comunicacoes)}")
                for i, com in enumerate(comunicacoes[:3]):
                    id_com = getattr(com, 'id', 'N/A')
                    tipo_com = getattr(com, 'tipoComunicacao', 'N/A')
                    teor = getattr(com, 'teor', None)
                    prazo = getattr(com, 'prazo', 'N/A')
                    dt_ref = getattr(com, 'dataReferencia', 'N/A')

                    print(f"\n    Comunicacao [{i+1}]:")
                    print(f"      ID: {id_com} | Tipo: {tipo_com}")
                    print(f"      Prazo: {prazo} | Data Ref: {dt_ref}")

                    if teor:
                        print(f"      >>> TEOR PRESENTE! len={len(teor)}")
                        print(f"      >>> Preview: {teor[:500]}...")
                        teor_path = OUTPUT_DIR / f"teor_{id_com}.html"
                        with open(teor_path, "w", encoding="utf-8") as f:
                            f.write(teor)
                        print(f"      >>> SALVO em: {teor_path}")
                    else:
                        print(f"      >>> Teor vazio")

                    # Documentos da comunicacao
                    docs_com = getattr(com, 'documento', []) or []
                    if docs_com:
                        print(f"      Documentos na comunicacao: {len(docs_com)}")
                        for doc in docs_com[:3]:
                            salvar_documento(doc, label=f"teor_{id_com}")
            else:
                print("  Nenhuma comunicacao retornada.")

        except Exception as e:
            print(f"  [ERRO] {type(e).__name__}: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  PoC FASE 2: RECUPERACAO DE INTEIRO TEOR")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)

    client = criar_cliente()

    estrategia_1_documento_especifico(client)
    estrategia_2_um_por_vez(client)
    estrategia_3_raw_xml(client)
    estrategia_4_teor_comunicacao(client)

    print("\n" + "=" * 70)
    print("  RESUMO")
    print("=" * 70)

    # Listar arquivos criados
    files = list(OUTPUT_DIR.glob("*"))
    if files:
        print(f"\n  Arquivos gerados em {OUTPUT_DIR}:")
        for f in sorted(files):
            size = f.stat().st_size
            print(f"    {f.name} ({size:,} bytes)")
    else:
        print("\n  Nenhum arquivo gerado.")

    print("\n  FIM")
