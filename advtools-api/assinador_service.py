import uuid
import hashlib
import os
import io
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import qrcode
try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    try:
        from PyPDF2 import PdfReader, PdfWriter
    except ImportError:
        PdfReader, PdfWriter = None, None

def gerar_token_unico() -> str:
    """Gera um token UUID seguro para link de assinatura, removendo traços."""
    return uuid.uuid4().hex

def calcular_hash_arquivo(caminho_arquivo: str) -> str:
    """Calcula o SHA256 do arquivo para garantir integridade."""
    if not os.path.exists(caminho_arquivo):
        return None
    
    sha256_hash = hashlib.sha256()
    with open(caminho_arquivo, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def gerar_certificado_pdf(dados_documento: dict, signatarios: list, caminho_saida: str, url_validacao: str = None) -> str:
    """
    Gera uma página PDF contendo o 'Manifesto de Assinaturas' (Log de Auditoria).
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
        if y < 150: 
            c.showPage()
            y = height - 50
            
        status = sig.get('status', 'Pendente')
        cor_status = colors.green if status == 'Assinado' else colors.red
        tipo = sig.get('tipo_autenticacao', 'assinatura')
        
        c.setFont("Helvetica-Bold", 11)
        c.drawString(60, y, f"{sig.get('nome', '')} ({sig.get('email', '')})")
        
        c.setFillColor(cor_status)
        c.drawString(400, y, status.upper())
        c.setFillColor(colors.black)
        y -= 15
        
        if status == 'Assinado':
            c.setFont("Helvetica", 9)
            data_ass = sig.get('data_assinatura')
            data_ass_str = data_ass.strftime('%d/%m/%Y %H:%M:%S') if data_ass else 'N/A'
            c.drawString(80, y, f"Assinado em: {data_ass_str}")
            y -= 12
            c.drawString(80, y, f"IP: {sig.get('ip_assinatura', 'N/A')}")
            y -= 12
            user_agent = sig.get('user_agent_assinatura', 'N/A')
            c.drawString(80, y, f"Método: {tipo.upper() if tipo else 'N/A'} | User-Agent: {user_agent[:40]}...")
            y -= 5
            
            img_path = sig.get('imagem_assinatura_path')
            if img_path and os.path.exists(img_path):
                try:
                    if tipo == 'selfie':
                        c.drawImage(img_path, 80, y - 85, width=110, height=82, mask='auto')
                        y -= 90
                    else:
                        c.drawImage(img_path, 80, y - 50, width=150, height=45, mask='auto')
                        y -= 60
                except Exception as e:
                    c.drawString(80, y - 10, f"[Erro ao carregar imagem: {e}]")
                    y -= 20
            else:
                 y -= 10
                 
            y -= 20 
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

def anexar_certificado(caminho_pdf_original: str, caminho_certificado: str, caminho_final: str) -> str:
    """Mescla o PDF original com a página de certificado no final."""
    if PdfWriter is None:
        raise ImportError("Biblioteca pypdf não instalada.")

    writer = PdfWriter()
    
    with open(caminho_pdf_original, "rb") as f_orig:
        reader_orig = PdfReader(f_orig)
        for page in reader_orig.pages:
            writer.add_page(page)
            
    with open(caminho_certificado, "rb") as f_cert:
        reader_cert = PdfReader(f_cert)
        for page in reader_cert.pages:
            writer.add_page(page)
            
    with open(caminho_final, "wb") as f_out:
        writer.write(f_out)
        
    return caminho_final

def estampar_assinaturas(caminho_pdf_original: str, signatarios: list, caminho_final: str) -> str:
    """Sobrepõe as imagens das assinaturas nas coordenadas salvas (pypdf origin 0,0 is bottom-left)."""
    if PdfWriter is None:
        raise ImportError("Biblioteca pypdf não instalada.")

    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=A4)
    
    sigs_by_page = {}
    for sig in signatarios:
        if not sig.get('imagem_assinatura_path') or not sig.get('pos_page'):
            continue
        page = int(sig['pos_page'])
        if page not in sigs_by_page:
            sigs_by_page[page] = []
        sigs_by_page[page].append(sig)
        
    if not sigs_by_page:
        # Se não houver assinaturas posicionadas, ignora estampas visuais
        return caminho_pdf_original 

    reader = PdfReader(caminho_pdf_original)
    writer = PdfWriter()

    for i, page in enumerate(reader.pages):
        page_num = i + 1
        
        if page_num in sigs_by_page:
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)
            
            packet_page = io.BytesIO()
            c_page = canvas.Canvas(packet_page, pagesize=(page_width, page_height))
            
            for sig in sigs_by_page[page_num]:
                img_path = sig['imagem_assinatura_path']
                
                doc_visual_w = float(sig.get('pos_doc_width', 0) or page_width)
                doc_visual_h = float(sig.get('pos_doc_height', 0) or page_height)
                
                scale_x = page_width / doc_visual_w
                scale_y = page_height / doc_visual_h
                
                x_pdf = float(sig['pos_x']) * scale_x
                
                # Invertendo Eixo Y pois o pypdf é (0,0) no canto inferior esquerdo
                # y_pos recebido do HTML assume (0,0) no topo superior esquerdo
                y_visual_invertido = doc_visual_h - float(sig['pos_y']) - float(sig['pos_height'])
                y_pdf = y_visual_invertido * scale_y
                
                w_pdf = float(sig['pos_width']) * scale_x
                h_pdf = float(sig['pos_height']) * scale_y
                
                try:
                    nome = sig.get('nome', 'Assinado Digitalmente')
                    font_size_base = h_pdf * 0.25
                    font_size_base = max(4, min(font_size_base, 10))
                    
                    min_w_needed = len(nome[:60]) * font_size_base * 0.65 + 15
                    if w_pdf < min_w_needed:
                        w_pdf = min_w_needed

                    # Caixa branca com borda preta
                    c_page.setFillColorRGB(1, 1, 1)
                    c_page.setStrokeColorRGB(0, 0, 0)
                    c_page.setLineWidth(0.5)
                    c_page.rect(x_pdf, y_pdf, w_pdf, h_pdf, fill=1, stroke=1)
                    
                    c_page.setFillColorRGB(0, 0, 0)
                    font_size = max(4, min(h_pdf * 0.25, 10))
                    
                    cpf = sig.get('cpf', 'CPF não informado')
                    margin = 5
                    
                    c_page.setFont("Helvetica-Oblique", font_size * 0.8)
                    c_page.drawString(x_pdf + margin, y_pdf + h_pdf - margin - (font_size * 0.8), "Assinado Digitalmente por:")
                    
                    c_page.setFont("Helvetica-Bold", font_size)
                    c_page.drawString(x_pdf + margin, y_pdf + (h_pdf/2) - (font_size/2), nome[:60])
                    
                    c_page.setFont("Helvetica", font_size * 0.9)
                    c_page.drawString(x_pdf + margin, y_pdf + margin, f"CPF: {cpf}")

                except Exception as e:
                    print(f"Erro ao estampar texto no PDF: {e}")

            c_page.save()
            packet_page.seek(0)
            
            overlay_pdf = PdfReader(packet_page)
            overlay_page = overlay_pdf.pages[0]
            page.merge_page(overlay_page)
            
        writer.add_page(page)

    with open(caminho_final, "wb") as f_out:
        writer.write(f_out)
        
    return caminho_final
