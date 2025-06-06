# Imagem base
FROM python:3.11-slim

# Diretório de trabalho
WORKDIR /app

# Copiar arquivos e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expor a porta usada pelo Streamlit (interna, não necessariamente a pública)
EXPOSE 8501

# Comando para iniciar o app Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
