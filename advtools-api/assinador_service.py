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

def calcular_hash_bytes(data: bytes) -> str:
    """Calcula o SHA256 de dados em memória."""
    sha256_hash = hashlib.sha256()
    sha256_hash.update(data)
    return sha256_hash.hexdigest()

def gerar_certificado_pdf(dados_documento: dict, signatarios: list, caminho_saida: str = None, url_validacao: str = None) -> bytes:
    """
    Gera uma página PDF contendo o 'Manifesto de Assinaturas' (Log de Auditoria).
    Se caminho_saida for None, retorna os bytes do PDF.
    """
    output = caminho_saida if caminho_saida else io.BytesIO()
    c = canvas.Canvas(output, pagesize=A4)
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
            
            # Imagem da Assinatura/Selfie no certificado
            img_path = sig.get('imagem_assinatura_path')
            if img_path:
                full_img_path = str(img_path)
                if not os.path.exists(full_img_path) and not full_img_path.startswith("static"):
                     full_img_path = os.path.join("static", full_img_path)

                if os.path.exists(full_img_path):
                    try:
                        if tipo == 'selfie':
                            c.drawImage(full_img_path, 80, y - 85, width=110, height=82, mask='auto')
                            y -= 90
                        else:
                            c.drawImage(full_img_path, 80, y - 50, width=150, height=45, mask='auto')
                            y -= 60
                    except Exception as e:
                        c.drawString(80, y - 10, f"[Erro ao carregar imagem: {e}]")
                        y -= 20
                else:
                     y -= 10
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
    if caminho_saida is None:
        return output.getvalue()
    return caminho_saida

def anexar_certificado(caminho_pdf_original: str, caminho_certificado: str, caminho_final: str) -> str:
    """Mescla o PDF original com a página de certificado no final."""
    if PdfWriter is None:
        raise ImportError("Biblioteca pypdf não instalada.")

    writer = PdfWriter()
    
    with open(caminho_pdf_original, "rb") as f_orig, open(caminho_certificado, "rb") as f_cert, open(caminho_final, "wb") as f_out:
        reader_orig = PdfReader(f_orig)
        for page in reader_orig.pages:
            writer.add_page(page)
            
        reader_cert = PdfReader(f_cert)
        for page in reader_cert.pages:
            writer.add_page(page)
            
        writer.write(f_out)
        
    return caminho_final

def estampar_assinaturas(pdf_puxar, signatarios: list, caminho_final: str = None):
    """
    Sobrepõe as imagens das assinaturas nas coordenadas salvas.
    pdf_puxar: pode ser bytes ou caminho do arquivo.
    Se caminho_final for None, retorna os bytes do PDF resultante.
    """
    if PdfWriter is None:
        raise ImportError("Biblioteca pypdf não instalada.")

    input_stream = io.BytesIO(pdf_puxar) if isinstance(pdf_puxar, bytes) else open(pdf_puxar, "rb")
    output_stream = caminho_final if caminho_final else io.BytesIO()

    try:
        reader = PdfReader(input_stream)
        writer = PdfWriter()
        
        # Agrupar assinaturas por página
        sigs_by_page = {}
        for sig in signatarios:
            if not sig.get('pos_page'): continue
            p = int(sig['pos_page'])
            if p not in sigs_by_page: sigs_by_page[p] = []
            sigs_by_page[p].append(sig)

        for i, page in enumerate(reader.pages):
            page_num = i + 1
            
            if page_num in sigs_by_page:
                page_width = float(page.mediabox.width)
                page_height = float(page.mediabox.height)
                
                packet_page = io.BytesIO()
                c_page = canvas.Canvas(packet_page, pagesize=(page_width, page_height))
                
                for sig in sigs_by_page[page_num]:
                    img_data = sig.get('imagem_bytes') 
                    # img_data: se não passar bytes, tentamos ler do path se for local
                    if not img_data and sig.get('imagem_assinatura_path'):
                         try:
                             ipath = str(sig['imagem_assinatura_path'])
                             possibilities = [ipath, os.path.join("static", ipath)]
                             for p in possibilities:
                                 if os.path.exists(p):
                                     with open(p, "rb") as fi:
                                         img_data = fi.read()
                                     break
                         except: pass
                    
                    if not img_data: continue # Sem imagem, não estampa
                    
                    # Usamos ImageReader para ler os bytes
                    img_reader = ImageReader(io.BytesIO(img_data))
                    
                    doc_visual_w = float(sig.get('pos_doc_width', 0) or page_width)
                    doc_visual_h = float(sig.get('pos_doc_height', 0) or page_height)
                    
                    scale_x = page_width / doc_visual_w
                    scale_y = page_height / doc_visual_h
                    
                    x_pdf = float(sig['pos_x']) * scale_x
                    y_visual_invertido = doc_visual_h - float(sig['pos_y']) - float(sig['pos_height'])
                    y_pdf = y_visual_invertido * scale_y
                    
                    w_pdf = float(sig['pos_width']) * scale_x
                    h_pdf = float(sig['pos_height']) * scale_y
                    
                    try:
                        nome = sig.get('nome', 'Assinado Digitalmente')
                        cpf = sig.get('cpf', 'CPF não informado')
                        tipo = sig.get('tipo_autenticacao', 'assinatura')
                        
                        # Cores e Estilos
                        c_page.setFillColorRGB(0.98, 0.98, 0.98) # Fundo quase branco
                        c_page.setStrokeColorRGB(0.85, 0.85, 0.85) # Borda suave
                        c_page.setLineWidth(0.5)
                        
                        # Desenha o Box (Carimbo) com a área total selecionada
                        c_page.roundRect(x_pdf, y_pdf, w_pdf, h_pdf, radius=4, fill=1, stroke=1)
                        
                        # Margens internas
                        padding = 4
                        
                        # Espaço para imagem (se for assinatura/desenho)
                        # Se for selfie, geralmente não estampamos no doc por privacidade (fica no certificado)
                        mostrar_img = (tipo == 'assinatura') and img_data
                        
                        img_w = 0
                        if mostrar_img:
                            # Divide o box: 40% imagem, 60% texto (ou proporcional)
                            img_w_max = w_pdf * 0.35 
                            img_h_max = h_pdf - (padding * 2)
                            
                            # Mantém proporção da imagem se possível
                            # drawImage com preserveAspectRatio
                            c_page.drawImage(img_reader, x_pdf + padding, y_pdf + padding, width=img_w_max, height=img_h_max, mask='auto', preserveAspectRatio=True, anchor='c')
                            img_w = img_w_max + padding
                        
                        # Texto ao lado ou ocupando tudo
                        text_x = x_pdf + padding + img_w
                        text_w_max = w_pdf - (padding * 2) - img_w
                        
                        # Fontes baseadas na altura disponível
                        # Se h_pdf for pequeno, diminuímos a fonte
                        base_font_size = min(7.0, h_pdf / 4.5)
                        
                        c_page.setFillColorRGB(0.3, 0.35, 0.4) 
                        c_page.setFont("Helvetica-Oblique", base_font_size * 0.8)
                        y_cursor = y_pdf + h_pdf - padding - (base_font_size * 0.8)
                        c_page.drawString(text_x, y_cursor, "Assinado Eletronicamente")
                        
                        y_cursor -= (base_font_size + 1.5)
                        c_page.setFillColorRGB(0.1, 0.15, 0.2)
                        c_page.setFont("Helvetica-Bold", base_font_size)
                        # Trunca nome se for muito longo para a largura
                        nome_display = nome[:40]
                        c_page.drawString(text_x, y_cursor, nome_display)
                        
                        y_cursor -= (base_font_size * 0.9 + 1.5)
                        c_page.setFillColorRGB(0.3, 0.35, 0.4) 
                        c_page.setFont("Helvetica", base_font_size * 0.8)
                        c_page.drawString(text_x, y_cursor, f"Doc: {cpf}")

                    except Exception as e:
                        print(f"Erro ao estampar assinatura no PDF: {e}")

                c_page.save()
                packet_page.seek(0)
                overlay_pdf = PdfReader(packet_page)
                page.merge_page(overlay_pdf.pages[0])
                
            writer.add_page(page)

        writer.write(output_stream)
    finally:
        if not isinstance(pdf_puxar, bytes):
            input_stream.close()

    if caminho_final is None:
        return output_stream.getvalue()
    return caminho_final
