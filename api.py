import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Body
from pydantic import BaseModel, HttpUrl, EmailStr
from storage import PostStorage
from fb_api import get_facebook_post_status
from apscheduler.schedulers.background import BackgroundScheduler
import requests  # para envio de webhook
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import sqlite3
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Carrega variáveis de ambiente
load_dotenv()

# Configurações de segurança e hashing
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def authenticate_user(email: str, password: str):
    user = storage.get_user(email)
    if not user or not verify_password(password, user["password_hash"]):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Valida JWT e retorna usuário ou HTTP 401 com mensagem amigável."""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            raise credentials_exception
    except JWTError:
        # Já retorna mensagem amigável
        raise credentials_exception
    user = storage.get_user(email)
    if not user:
        raise credentials_exception
    return user

# Configura logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(title="Facebook Monitor API")

# CORS: permite Preflight e chamadas de outras origens
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Handler global para HTTPException com formato de resposta uniforme
@app.exception_handler(HTTPException)
async def http_error_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
        headers=exc.headers or {}
    )

storage = PostStorage()
scheduler = BackgroundScheduler()

# JSON body para registro/login espera { username: email, password }
class UserCreate(BaseModel):
    username: EmailStr
    password: str

# Define schemas para endpoints
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

@app.post("/register", status_code=201)
def register(user: UserCreate = Body(...)):
    """Registro de usuário via JSON"""
    email, password = user.username, user.password
    try:
        hashed = get_password_hash(password)
        user_id = storage.register_user(email, hashed)
        access_token = create_access_token(data={"sub": email, "user_id": user_id})
        return {"msg": "User registered", "user_id": user_id, "access_token": access_token, "token_type": "bearer"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already registered")

@app.post("/login")
def login(user: UserCreate = Body(...)):
    """Login de usuário via JSON"""
    auth = authenticate_user(user.username, user.password)
    if not auth:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token = create_access_token(data={"sub": auth["email"], "user_id": auth["id"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/posts", status_code=201)
def add_post(post: PostURL, current_user=Depends(get_current_user)):
    """
    Adiciona uma URL de post se ativa.
    """
    try:
        if not get_facebook_post_status(post.url):
            raise HTTPException(status_code=400, detail="Post inativo ou inexistente")
        added = storage.add(post.url, current_user["id"])
        if not added:
            raise HTTPException(status_code=409, detail="URL já monitorada")
        logging.info(f"Post adicionado via API: {post.url}")
        return {"url": post.url}
    except ValueError as ve:
        logging.error(f"URL inválida: {ve}")
        raise HTTPException(status_code=422, detail=str(ve))

@app.get("/posts")
def list_posts(current_user=Depends(get_current_user)):
    """
    Lista todas as URLs monitoradas.
    """
    urls = storage.list_user_posts(current_user["id"])
    return {"posts": urls}

@app.post("/config/webhook", status_code=200)
def set_webhook(config: WebhookConfig, current_user=Depends(get_current_user)):
    """Configura URL de webhook para notificações"""
    storage.set_webhook(current_user["id"], str(config.url))
    logging.info(f"Webhook configurado: {config.url}")
    return {"webhook": str(config.url)}

@app.get("/config/webhook")
def get_webhook(current_user=Depends(get_current_user)):
    """Retorna webhook configurado, se existir"""
    url = storage.get_webhook(current_user["id"])
    if not url:
        raise HTTPException(status_code=404, detail="Webhook não configurado")
    return {"webhook": url}

@app.get("/config/webhook/verify", status_code=200)
def verify_webhook(current_user=Depends(get_current_user)):
    """Verifica se o webhook configurado está funcionando corretamente."""
    url = storage.get_webhook(current_user["id"])
    if not url:
        raise HTTPException(status_code=404, detail="Webhook não configurado")
    try:
        resp = requests.post(url, json={"type": "verification"})
        if resp.status_code >= 400:
            raise HTTPException(status_code=400, detail=f"Webhook respondeu com status {resp.status_code}")
    except Exception as e:
        logging.error(f"Erro ao verificar webhook: {e}")
        raise HTTPException(status_code=400, detail="Falha ao conectar no webhook")
    return {"status": "ok", "webhook": url}

def send_inactive_webhook(post_url: str, user_id: int):
    webhook_url = storage.get_webhook(user_id)
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
    for user_id, url in storage.list_all_posts():
        active = get_facebook_post_status(url)
        if not active:
            logging.error(f"Post inativo detectado para usuário {user_id}: {url}. Removendo.")
            storage.remove(url, user_id)
            send_inactive_webhook(url, user_id)

@app.on_event("startup")
async def start_scheduler():
    scheduler.add_job(check_all_posts, 'interval', minutes=3)
    scheduler.start()
    logging.info("Scheduler iniciado.")

@app.on_event("shutdown")
async def shutdown_scheduler():
    scheduler.shutdown()
    logging.info("Scheduler encerrado.")
