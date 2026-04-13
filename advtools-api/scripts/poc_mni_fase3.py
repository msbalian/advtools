"""
PoC Fase 3: Investigacao profunda do conteudo MNI
- XML completo com documentos
- consultarTeorComunicacao com processo correto
- Buscar se ha endpoint alternativo para download
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from lxml import etree

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(env_path)

PROJUDI_USER = os.getenv("PROJUDI_USER", "")
PROJUDI_PASSWORD = os.getenv("PROJUDI_PASSWORD", "")
WSDL_URL = "https://projudi.tjgo.jus.br/IntercomunicacaoService?WSDL"
PROCESSO_TESTE = "57602432220258090051"

OUTPUT_DIR = Path(__file__).parent / "poc_output"
OUTPUT_DIR.mkdir(exist_ok=True)


def criar_cliente_debug():
    from zeep import Client
    from zeep.settings import Settings
    from zeep.plugins import HistoryPlugin
    settings = Settings(strict=False, xml_huge_tree=True)
    history = HistoryPlugin()
    client = Client(wsdl=WSDL_URL, settings=settings, plugins=[history])
    return client, history


def teste_xml_completo():
    """Pega o XML bruto completo da consulta COM documentos."""
    print("\n" + "=" * 70)
    print("  TESTE A: XML completo com incluirDocumentos=true")
    print("=" * 70)

    client, history = criar_cliente_debug()

    try:
        response = client.service.consultarProcesso(
            idConsultante=PROJUDI_USER,
            senhaConsultante=PROJUDI_PASSWORD,
            numeroProcesso=PROCESSO_TESTE,
            movimentos=True,
            incluirCabecalho=True,
            incluirDocumentos=True
        )

        print(f"  sucesso: {response.sucesso}")

        last = history.last_received
        if last and 'envelope' in last:
            xml_str = etree.tostring(last['envelope'], pretty_print=True, encoding='unicode')
            xml_path = OUTPUT_DIR / "full_response_with_docs.xml"
            with open(xml_path, "w", encoding="utf-8") as f:
                f.write(xml_str)
            print(f"  XML total: {len(xml_str):,} chars")
            print(f"  Salvo em: {xml_path}")

            # Contar tags documento
            doc_count = xml_str.count("<ns3:documento ") + xml_str.count("<documento ")
            print(f"  Tags <documento> encontradas: {doc_count}")

            # Procurar conteudo
            if "conteudo" in xml_str:
                print("  >>> Tag 'conteudo' ENCONTRADA no XML!")
                idx = xml_str.index("conteudo")
                print(f"  >>> Contexto: ...{xml_str[max(0,idx-100):idx+200]}...")
            else:
                print("  >>> Tag 'conteudo' NAO presente no XML")

            # Verificar atributos dos documentos
            print("\n  Amostra dos primeiros 3 documentos (atributos):")
            root = last['envelope']
            ns = {'ns3': 'http://www.cnj.jus.br/intercomunicacao-2.2.2'}
            docs_xml = root.findall('.//ns3:documento', ns)
            for i, doc_el in enumerate(docs_xml[:3]):
                print(f"    Doc [{i+1}]:")
                for attr, val in doc_el.attrib.items():
                    print(f"      {attr}: {val}")
                # Filhos
                for child in doc_el:
                    tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                    text_preview = (child.text or '')[:100] if child.text else '(vazio)'
                    has_children = len(child) > 0
                    print(f"      [{tag}] text={text_preview} | filhos={has_children}")

        # Conferir movimentacoes com documentos vinculados
        proc = response.processo
        movs = getattr(proc, 'movimento', []) or []
        movs_com_docs = [m for m in movs if getattr(m, 'idDocumentoVinculado', None)]
        print(f"\n  Movimentacoes com docs vinculados: {len(movs_com_docs)}/{len(movs)}")
        for mov in movs_com_docs[:5]:
            dt = getattr(mov, 'dataHora', '')
            docs_ids = getattr(mov, 'idDocumentoVinculado', [])
            mov_loc = getattr(mov, 'movimentoLocal', None)
            desc = getattr(mov_loc, 'descricao', '') if mov_loc else ''
            print(f"    {dt} | {desc} | docs: {docs_ids}")

    except Exception as e:
        print(f"  [ERRO] {type(e).__name__}: {e}")


def teste_teor_comunicacao_corrigido():
    """Tenta consultarTeorComunicacao buscando primeiro os avisos de cada processo."""
    print("\n" + "=" * 70)
    print("  TESTE B: consultarTeorComunicacao (corrigido)")
    print("  Primeiro busca avisos, depois pede o teor do mesmo processo")
    print("=" * 70)

    from zeep import Client
    from zeep.settings import Settings
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, settings=settings)

    # Buscar avisos pendentes
    try:
        avisos_resp = client.service.consultarAvisosPendentes(
            idConsultante=PROJUDI_USER,
            senhaConsultante=PROJUDI_PASSWORD,
            idRepresentado=PROJUDI_USER
        )

        avisos = getattr(avisos_resp, 'aviso', []) or []
        print(f"  Avisos encontrados: {len(avisos)}")

        for aviso in avisos[:3]:
            id_aviso = getattr(aviso, 'idAviso', '')
            proc_obj = getattr(aviso, 'processo', None)
            if not proc_obj:
                continue
            
            num_proc = getattr(proc_obj, 'numero', '')
            tipo_com = getattr(aviso, 'tipoComunicacao', '')
            data_disp = getattr(aviso, 'dataDisponibilizacao', '')

            # O numero ja vem formatado no aviso
            num_limpo = num_proc.replace(".", "").replace("-", "")

            print(f"\n  >>> Tentando teor do aviso {id_aviso}")
            print(f"      Processo: {num_proc} (limpo: {num_limpo})")
            print(f"      Tipo: {tipo_com} | Data: {data_disp}")

            try:
                teor_resp = client.service.consultarTeorComunicacao(
                    idConsultante=PROJUDI_USER,
                    senhaConsultante=PROJUDI_PASSWORD,
                    numeroProcesso=num_limpo,
                    identificadorAviso=str(id_aviso)
                )

                print(f"      sucesso: {teor_resp.sucesso}")
                print(f"      mensagem: {teor_resp.mensagem}")

                comunicacoes = getattr(teor_resp, 'comunicacao', []) or []
                if comunicacoes:
                    print(f"      Comunicacoes: {len(comunicacoes)}")
                    for com in comunicacoes[:2]:
                        teor = getattr(com, 'teor', None)
                        id_com = getattr(com, 'id', 'N/A')
                        tipo_prazo = getattr(com, 'tipoPrazo', '')
                        prazo = getattr(com, 'prazo', '')

                        print(f"        ID: {id_com} | Prazo: {prazo} {tipo_prazo}")

                        if teor:
                            print(f"        >>> TEOR ENCONTRADO! len={len(teor)}")
                            preview = teor[:300].replace('\n', ' ')
                            print(f"        >>> Preview: {preview}...")
                            
                            teor_path = OUTPUT_DIR / f"teor_aviso_{id_aviso}.html"
                            with open(teor_path, "w", encoding="utf-8") as f:
                                f.write(teor)
                            print(f"        >>> SALVO: {teor_path}")
                        else:
                            print(f"        >>> Teor vazio")

                        # Documentos anexos a comunicacao
                        docs = getattr(com, 'documento', []) or []
                        if docs:
                            print(f"        Documentos na comunicacao: {len(docs)}")
                            for doc in docs:
                                id_doc = getattr(doc, 'idDocumento', '')
                                desc = getattr(doc, 'descricao', '')
                                conteudo = getattr(doc, 'conteudo', None)
                                print(f"          doc ID={id_doc}, desc={desc}, conteudo={'SIM' if conteudo else 'NAO'}")

            except Exception as e2:
                print(f"      [ERRO] {type(e2).__name__}: {e2}")

    except Exception as e:
        print(f"  [ERRO] {type(e).__name__}: {e}")


def teste_download_direto():
    """Tenta acessar documento por URL direta do PROJUDI."""
    print("\n" + "=" * 70)
    print("  TESTE C: Tentativa de acesso direto via HTTP")
    print("  Verificando se ha endpoint REST para download")
    print("=" * 70)

    import requests

    # Patterns comuns de download no PROJUDI
    doc_id = "516529955"
    urls_tentativa = [
        f"https://projudi.tjgo.jus.br/DocumentoServlet?documentoId={doc_id}",
        f"https://projudi.tjgo.jus.br/BuscaArquivo?documentoId={doc_id}",
        f"https://projudi.tjgo.jus.br/api/documento/{doc_id}",
    ]

    for url in urls_tentativa:
        print(f"\n  Tentando: {url}")
        try:
            resp = requests.get(url, timeout=10, allow_redirects=True)
            print(f"    Status: {resp.status_code}")
            print(f"    Content-Type: {resp.headers.get('Content-Type', 'N/A')}")
            print(f"    Content-Length: {resp.headers.get('Content-Length', 'N/A')}")
            if resp.status_code == 200:
                preview = resp.text[:200] if resp.text else "(vazio)"
                print(f"    Preview: {preview}")
        except Exception as e:
            print(f"    [ERRO] {e}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  PoC FASE 3: INVESTIGACAO PROFUNDA")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)

    teste_xml_completo()
    teste_teor_comunicacao_corrigido()
    teste_download_direto()

    print("\n" + "=" * 70)
    print("  ARQUIVOS GERADOS:")
    print("=" * 70)
    for f in sorted(OUTPUT_DIR.glob("*")):
        print(f"    {f.name} ({f.stat().st_size:,} bytes)")

    print("\n  FIM")
