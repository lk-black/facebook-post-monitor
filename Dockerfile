# Dockerfile para Facebook Monitor API
FROM python:3.10-slim

# Diretório de trabalho
WORKDIR /app

# Instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código
COPY . .

# Variável para banco SQLite
ENV STORAGE_DB_PATH=/app/posts.db

# Define default PORT for Render
ENV PORT 8000

# Porta padrão
EXPOSE 8000

# Comando para rodar a aplicação
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT}"]
