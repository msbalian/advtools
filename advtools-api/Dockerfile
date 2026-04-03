# Usar imagem oficial do Python 3.12 slim para um build menor
FROM python:3.12-slim

# Definir variáveis de ambiente para o Python (não gravar bytecode e não usar buffer no stdout/stderr)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Definir o diretório de trabalho no container
WORKDIR /app

# Copiar os arquivos de requisitos primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instalar LibreOffice (necessário para conversão DOCX → PDF em Linux)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice-writer \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copiar o restante do código da API
COPY . .

# Expor a porta em que a aplicação vai rodar
EXPOSE 8000

# Script de entrada formatado
CMD ["sh", "-c", "alembic upgrade head && gunicorn main:app -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000"]
