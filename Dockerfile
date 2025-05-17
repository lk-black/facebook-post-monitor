# Dockerfile para Facebook Monitor API
FROM python:3.10-slim

# Diretório de trabalho
WORKDIR /app

# Instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código
COPY . .

# Cria o diretório onde o disco será montado
RUN mkdir -p /data

# Aponta o SQLite para dentro do disco montado
ENV STORAGE_DB_PATH=/data/posts.db

# Render expõe a $PORT; sobra definir uma default
ENV PORT=8000

# Porta padrãoS
EXPOSE 8000

# Comando para rodar a aplicação
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT}"]
