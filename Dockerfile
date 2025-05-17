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

# Porta padrão
EXPOSE 8000

# Comando para rodar a aplicação
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
