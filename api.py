import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from storage import PostStorage
from fb_api import get_facebook_post_status
from apscheduler.schedulers.background import BackgroundScheduler
import requests  # para envio de webhook

# Carrega variáveis de ambiente
load_dotenv()

# Configura logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(title="Facebook Monitor API")
storage = PostStorage()
scheduler = BackgroundScheduler()

class PostURL(BaseModel):
    url: str

class WebhookConfig(BaseModel):
    url: HttpUrl

@app.get("/health", status_code=200)
def health():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}

@app.post("/posts", status_code=201)
def add_post(post: PostURL):
    """
    Adiciona uma URL de post se ativa.
    """
    try:
        if not get_facebook_post_status(post.url):
            raise HTTPException(status_code=400, detail="Post inativo ou inexistente")
        added = storage.add(post.url)
        if not added:
            raise HTTPException(status_code=409, detail="URL já monitorada")
        logging.info(f"Post adicionado via API: {post.url}")
        return {"url": post.url}
    except ValueError as ve:
        logging.error(f"URL inválida: {ve}")
        raise HTTPException(status_code=422, detail=str(ve))

@app.get("/posts")
def list_posts():
    """
    Lista todas as URLs monitoradas.
    """
    return {"posts": storage.list_all()}

@app.post("/config/webhook", status_code=200)
def set_webhook(config: WebhookConfig):
    """Configura URL de webhook para notificações"""
    storage.set_webhook(str(config.url))
    logging.info(f"Webhook configurado: {config.url}")
    return {"webhook": str(config.url)}

@app.get("/config/webhook")
def get_webhook():
    """Retorna webhook configurado, se existir"""
    url = storage.get_webhook()
    if not url:
        raise HTTPException(status_code=404, detail="Webhook não configurado")
    return {"webhook": url}

def send_inactive_webhook(post_url: str):
    webhook_url = storage.get_webhook()
    if not webhook_url:
        return
    try:
        resp = requests.post(webhook_url, json={"url": post_url, "status": "inactive"})
        if resp.status_code >= 400:
            logging.error(f"Falha ao enviar webhook ({resp.status_code}): {resp.text}")
    except Exception as e:
        logging.error(f"Erro no envio de webhook: {e}")

def check_all_posts():
    """
    Job que verifica todos os posts monitorados.
    """
    for url in storage.list_all():
        active = get_facebook_post_status(url)
        if not active:
            logging.error(f"Post inativo detectado no agendador: {url}. Removendo.")
            storage.remove(url)
            send_inactive_webhook(url)

@app.on_event("startup")
async def start_scheduler():
    scheduler.add_job(check_all_posts, 'interval', minutes=5)
    scheduler.start()
    logging.info("Scheduler iniciado.")

@app.on_event("shutdown")
async def shutdown_scheduler():
    scheduler.shutdown()
    logging.info("Scheduler encerrado.")
