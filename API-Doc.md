<!-- filepath: /home/lk/Personal-Projects/facebook-monitor/API-Doc.md -->
# Facebook Post Monitor API Documentation

**Base URL:** `https://facebook-post-monitor.onrender.com/`

---

## 1. Health Check

### GET /health
Verifica se a API está funcionando.

**Request:**
```
GET /health HTTP/1.1
Host: facebook-post-monitor.onrender.com
```

**Response:**
- Status: `200 OK`
```json
{ "status": "healthy" }
```

---

## 2. Registro de Usuário

### POST /register
Cadastra um novo usuário.

**Request:**
```
POST /register HTTP/1.1
Host: facebook-post-monitor.onrender.com
Content-Type: application/json
```
**Body:**
```json
{
  "username": "user@example.com",
  "password": "suaSenha"
}
```

**Responses:**
- `201 Created`: usuário cadastrado com sucesso.
```json
{
  "msg": "User registered",
  "user_id": 1,
  "access_token": "<JWT_TOKEN>",
  "refresh_token": "<REFRESH_TOKEN>",
  "token_type": "bearer"
}
```
- `400 Bad Request`: email já registrado.
```json
{ "error": "Email already registered" }
```

---

## 3. Login

### POST /login
Autentica usuário e retorna token JWT.

**Request:**
```
POST /login HTTP/1.1
Host: facebook-post-monitor.onrender.com
Content-Type: application/json
```
**Body:**
```json
{
  "username": "user@example.com",
  "password": "suaSenha"
}
```

**Responses:**
- `200 OK`: login bem-sucedido.
```json
{
  "access_token": "<JWT_TOKEN>",
  "refresh_token": "<REFRESH_TOKEN>",
  "token_type": "bearer"
}
```
- `401 Unauthorized`: credenciais inválidas.
```json
{ "error": "Incorrect email or password" }
```

---

## 3.1 Refresh Token

### POST /refresh_token
Gera um novo access_token a partir de um refresh_token válido.

**Request:**
```
POST /refresh_token HTTP/1.1
Host: facebook-post-monitor.onrender.com
Content-Type: application/json
```
**Body:**
```json
{
  "token": "<REFRESH_TOKEN>"
}
```

**Responses:**
- `200 OK`: token renovado.
```json
{
  "access_token": "<JWT_TOKEN>",
  "token_type": "bearer"
}
```
- `401 Unauthorized`: refresh_token inválido ou expirado.
```json
{ "error": "Refresh token inválido ou expirado" }
```

---

> **Nota:** Para os endpoints a seguir é necessário enviar o cabeçalho:
>```
>Authorization: Bearer <JWT_TOKEN>
>```

## 4. Posts Monitorados

### POST /posts
Adiciona uma URL de post do Facebook para monitoramento.

**Request:**
```
POST /posts HTTP/1.1
Host: facebook-post-monitor.onrender.com
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>
```
**Body:**
```json
{
  "url": "https://www.facebook.com/..." 
}
```

**Responses:**
- `201 Created`: post adicionado.
```json
{ "url": "https://www.facebook.com/..." }
```
- `400 Bad Request`: post inativo ou inexistente.
```json
{ "error": "Post inativo ou inexistente" }
```
- `409 Conflict`: URL já está sendo monitorada.
```json
{ "error": "URL já monitorada" }
```

### GET /posts
Lista todas as URLs de posts monitoradas pelo usuário.

**Request:**
```
GET /posts HTTP/1.1
Host: facebook-post-monitor.onrender.com
Authorization: Bearer <JWT_TOKEN>
```

**Response:**
- `200 OK`
```json
{ "posts": [
    "https://www.facebook.com/...",
    "https://www.facebook.com/..."
] }
```

### DELETE /posts/{post_url}
Remove uma URL de post monitorado da lista do usuário autenticado.

**Request:**
```
DELETE /posts/{post_url} HTTP/1.1
Host: facebook-post-monitor.onrender.com
Authorization: Bearer <JWT_TOKEN>
```

**Response:**
- `200 OK`: post removido.
```json
{ "msg": "Post removido", "url": "https://www.facebook.com/..." }
```
- `404 Not Found`: post não está na lista do usuário.
```json
{ "error": "Post não encontrado na sua lista" }
```

---

## 5. Configuração de Webhook

Para receber notificações quando um post ficar inativo, configure um webhook.

### POST /config/webhook
Define a URL do webhook.

**Request:**
```
POST /config/webhook HTTP/1.1
Host: facebook-post-monitor.onrender.com
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>
```
**Body:**
```json
{ "url": "https://meuservidor.com/webhook" }
```

**Response:**
- `200 OK`
```json
{ "webhook": "https://meuservidor.com/webhook" }
```

### GET /config/webhook
Retorna a URL do webhook configurado.

**Request:**
```
GET /config/webhook HTTP/1.1
Host: facebook-post-monitor.onrender.com
Authorization: Bearer <JWT_TOKEN>
```

**Responses:**
- `200 OK`: webhook configurado.
```json
{ "webhook": "https://meuservidor.com/webhook" }
```
- `404 Not Found`: webhook não configurado.
```json
{ "error": "Webhook não configurado" }
```

### POST /config/webhook/verify
Verifica se a URL do webhook está ativa.

**Request:**
```
POST /config/webhook/verify HTTP/1.1
Host: facebook-post-monitor.onrender.com
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>
```
**Body:**
```json
{ "url": "https://meuservidor.com/webhook" }
```

**Response:**
- `200 OK`
```json
{
  "webhook": "https://meuservidor.com/webhook",
  "active": true
}
```

---

## 6. Webhook de Inatividade

A cada 3 minutos, a API verifica todos os posts monitorados. Se um post estiver inativo, ele é removido e é enviado um POST ao webhook configurado com payload:
```json
{
  "url": "https://www.facebook.com/...",
  "status": "inactive"
}
```

---

## 7. Erros Comuns

- `401 Unauthorized`: token ausente, inválido ou expirado.
- `422 Unprocessable Entity`: formato de URL inválido.

---

*Documentação gerada em 2025*