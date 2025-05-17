import os
from dotenv import load_dotenv
import logging
import uvicorn

# Carrega variáveis de ambiente de .env (opcional em produção)
load_dotenv()

# Configura logging básico
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logging.info(f"Iniciando API no porta {port}")
    uvicorn.run("api:app", host="0.0.0.0", port=port)