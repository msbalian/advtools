import uuid
import hashlib
import os
import io
import json
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    # Tenta PyPDF2 caso pypdf não esteja instalado (fallback)
    try:
        from PyPDF2 import PdfReader, PdfWriter
    except ImportError:
        print("ERRO: Instale 'pypdf' ou 'PyPDF2' para manipulação de PDF.")
        PdfReader, PdfWriter = None, None

def gerar_token_unico():
    """Gera um token UUID seguro para link de assinatura, removendo traços."""
    return uuid.uuid4().hex

def calcular_hash_arquivo(caminho_arquivo):
    """Calcula o SHA256 do arquivo para garantir integridade."""
    if not os.path.exists(caminho_arquivo):
        return None
    
    sha256_hash = hashlib.sha256()
    with open(caminho_arquivo, "rb") as f:
        # Lê em blocos de 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

import qrcode
from reportlab.lib.utils import ImageReader

def gerar_certificado_pdf(dados_documento, signatarios, caminho_saida, url_validacao=None):
    """
    Gera uma página PDF contendo o 'Manifesto de Assinaturas' (Log de Auditoria).
    dados_documento: { 'nome': '...', 'hash_original': '...' }
    signatarios: Lista de dicts com dados da assinatura
    url_validacao: URL pública para validar o QR Code
    """
    c = canvas.Canvas(caminho_saida, pagesize=A4)
    width, height = A4
    
    # Cabeçalho
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Certificado de Assinatura Digital - ADVtools Sign")
    
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    c.drawString(50, height - 85, f"Documento: {dados_documento.get('nome', 'N/A')}")
    
    # QR Code de Validação
    if url_validacao:
        qr = qrcode.make(url_validacao)
        qr_img = io.BytesIO()
        qr.save(qr_img, format='PNG')
        qr_img.seek(0)
        
        # Desenha QR Code no canto superior direito
        c.drawImage(ImageReader(qr_img), width - 130, height - 130, width=100, height=100)
        c.setFont("Helvetica", 8)
        c.drawCentredString(width - 80, height - 140, "Verificar Autenticidade")
    
    # Hash Original
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, height - 110, "Hash do Documento Original (SHA256):")
    c.setFont("Courier", 9)
    c.drawString(50, height - 125, dados_documento.get('hash_original', 'N/A'))
    
    y = height - 170
    
    # Lista de Signatários
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Signatários")
    y -= 30
    
    for sig in signatarios:
        if y < 150: # Nova página se encher (espaço maior para selfie)
            c.showPage()
            y = height - 50
            
        status = sig.get('status', 'Pendente')
        cor_status = colors.green if status == 'Assinado' else colors.red
        tipo = sig.get('tipo_autenticacao', 'assinatura')
        
        c.setFont("Helvetica-Bold", 11)
        c.drawString(60, y, f"{sig['nome']} ({sig['email']})")
        
        # Status Badge
        c.setFillColor(cor_status)
        c.drawString(400, y, status.upper())
        c.setFillColor(colors.black)
        y -= 15
        
        if status == 'Assinado':
            c.setFont("Helvetica", 9)
            c.drawString(80, y, f"Assinado em: {sig.get('data_assinatura', 'N/A')}")
            y -= 12
            c.drawString(80, y, f"IP: {sig.get('ip_assinatura', 'N/A')}")
            y -= 12
            c.drawString(80, y, f"Método: {tipo.upper()} | User-Agent: {sig.get('user_agent_assinatura', 'N/A')[:40]}...")
            y -= 5
            
            # Imagem da Assinatura ou Selfie
            img_path = sig.get('imagem_assinatura_path')
            if img_path and os.path.exists(img_path):
                try:
                    # Se for selfie, desenha maior e mantendo proporção 4:3
                    if tipo == 'selfie':
                        c.drawImage(img_path, 80, y - 85, width=110, height=82, mask='auto')
                        y -= 90
                    else:
                        # Assinatura manuscrita (retangular)
                        c.drawImage(img_path, 80, y - 50, width=150, height=45, mask='auto')
                        y -= 60
                except Exception as e:
                    c.drawString(80, y - 10, f"[Erro ao carregar imagem: {e}]")
                    y -= 20
            else:
                 y -= 10
                 
            y -= 20 # Espaço extra
        else:
            c.setFont("Helvetica-Oblique", 9)
            c.drawString(80, y, "Aguardando assinatura...")
            y -= 30
            
    # Rodapé Legal
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.grey)
    c.drawString(50, 60, "Validação: " + (url_validacao if url_validacao else "N/A"))
    c.drawString(50, 50, "A validade jurídica deste documento é garantida pela Medida Provisória 2.200-2/2001 (ICP-Brasil).")
    c.save()
    return caminho_saida

def anexar_certificado(caminho_pdf_original, caminho_certificado, caminho_final):
    """
    Mescla o PDF original com a página de certificado no final.
    """
    if PdfWriter is None:
        raise ImportError("Biblioteca pypdf não instalada.")

    writer = PdfWriter()
    
    # Adiciona páginas do original
    with open(caminho_pdf_original, "rb") as f_orig:
        reader_orig = PdfReader(f_orig)
        for page in reader_orig.pages:
            writer.add_page(page)
            
    # Adiciona página do certificado
    with open(caminho_certificado, "rb") as f_cert:
        reader_cert = PdfReader(f_cert)
        for page in reader_cert.pages:
            writer.add_page(page)
            
    # Salva final
    with open(caminho_final, "wb") as f_out:
        writer.write(f_out)
        
    return caminho_final

def estampar_assinaturas(caminho_pdf_original, signatarios, caminho_final):
    """
    Sobrepõe as imagens das assinaturas nas coordenadas salvas.
    signatarios: Lista de dicts com { 'imagem_assinatura_path', 'page_number', 'x_pos', 'y_pos', 'width', 'height', 'docWidth', 'docHeight' }
    """
    if PdfWriter is None:
        raise ImportError("Biblioteca pypdf não instalada.")

    # 1. Cria um PDF temporário com as estampas para cada página
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=A4) # Tamanho base, será ajustado
    
    # Agrupa assinaturas por página
    sigs_by_page = {}
    for sig in signatarios:
        if not sig.get('imagem_assinatura_path') or not sig.get('page_number'):
            continue
        page = int(sig['page_number'])
        if page not in sigs_by_page:
            sigs_by_page[page] = []
        sigs_by_page[page].append(sig)
        
    # Se não houver assinaturas posicionadas, retorna o original (ou erro?)
    if not sigs_by_page:
        return caminho_pdf_original # Retorna sem alterações se não tiver coordenadas

    # 2. Processa o PDF original para saber o tamanho das páginas
    reader = PdfReader(caminho_pdf_original)
    writer = PdfWriter()

    for i, page in enumerate(reader.pages):
        page_num = i + 1
        
        if page_num in sigs_by_page:
            # Cria um canvas temporário do tamanho exato da página
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)
            
            packet_page = io.BytesIO()
            c_page = canvas.Canvas(packet_page, pagesize=(page_width, page_height))
            
            for sig in sigs_by_page[page_num]:
                img_path = sig['imagem_assinatura_path']
                
                # Check coordinates (always)
                doc_visual_w = float(sig.get('docWidth', 0) or 0)
                doc_visual_h = float(sig.get('docHeight', 0) or 0)
                
                if doc_visual_w <= 0: doc_visual_w = page_width
                if doc_visual_h <= 0: doc_visual_h = page_height
                
                scale_x = page_width / doc_visual_w
                scale_y = page_height / doc_visual_h
                
                # Converte posição e tamanho
                # X: Relativo * Escala
                x_pdf = float(sig['x_pos']) * scale_x
                
                # Y: (AlturaVisual - Y_Relativo - AlturaObj) * Escala
                # Invertendo o eixo Y
                y_visual_invertido = doc_visual_h - float(sig['y_pos']) - float(sig['height'])
                y_pdf = y_visual_invertido * scale_y
                
                w_pdf = float(sig['width']) * scale_x
                h_pdf = float(sig['height']) * scale_y
                
                print(f"DEBUG ESTAMPA: Page {page_num} | Sig {sig['id']} | Img={img_path} | X_PDF={x_pdf} Y_PDF={y_pdf}")

                try:
                    # Garantia de largura mínima baseada no nome (em PDF units)
                    # Heurística: aprox 60% do font_size por caractere + margens
                    nome = sig.get('nome', 'Assinado Digitalmente')
                    font_size_base = h_pdf * 0.25
                    if font_size_base < 4: font_size_base = 4
                    if font_size_base > 10: font_size_base = 10
                    
                    min_w_needed = len(nome[:60]) * font_size_base * 0.65 + 15
                    if w_pdf < min_w_needed:
                        w_pdf = min_w_needed

                    # Desenha Caixa (Fundo Branco + Borda)
                    c_page.setFillColorRGB(1, 1, 1) # Branco
                    c_page.setStrokeColorRGB(0, 0, 0) # Preto
                    c_page.setLineWidth(0.5)
                    c_page.rect(x_pdf, y_pdf, w_pdf, h_pdf, fill=1, stroke=1)
                    
                    # Foto removida do carimbo conforme solicitação do usuário
                    # A foto permanecerá apenas no certificado de autenticidade.

                    # Desenha Texto (SEMPRE)
                    c_page.setFillColorRGB(0, 0, 0)
                    
                    # Ajusta fonte baseada na altura da caixa (tentativa heurística)
                    font_size = h_pdf * 0.25 # 25% da altura
                    if font_size < 4: font_size = 4
                    if font_size > 10: font_size = 10
                    
                    c_page.setFont("Helvetica", font_size)
                    
                    cpf = sig.get('cpf', '')
                    if not cpf: cpf = "CPF não informado"
                    
                    # Calcula posições das linhas (de baixo para cima no PDF)
                    margin = 5 # Margem interna maior
                    
                    # Linha 3 (Topo): Titulo
                    c_page.setFont("Helvetica-Oblique", font_size * 0.8)
                    c_page.drawString(x_pdf + margin, y_pdf + h_pdf - margin - (font_size * 0.8), "Assinado Digitalmente por:")
                    
                    # Linha 2 (Meio): Nome
                    c_page.setFont("Helvetica-Bold", font_size)
                    c_page.drawString(x_pdf + margin, y_pdf + (h_pdf/2) - (font_size/2), nome[:60]) # Trunca se mto longo
                    
                    # Linha 1 (Base): CPF
                    c_page.setFont("Helvetica", font_size * 0.9)
                    c_page.drawString(x_pdf + margin, y_pdf + margin, f"CPF: {cpf}")

                except Exception as e:
                    print(f"Erro ao estampar texto: {e}")

            c_page.save()
            packet_page.seek(0)
            
            # Merge
            overlay_pdf = PdfReader(packet_page)
            overlay_page = overlay_pdf.pages[0]
            page.merge_page(overlay_page)
            
        writer.add_page(page)

    with open(caminho_final, "wb") as f_out:
        writer.write(f_out)
        
    return caminho_final
