# Documentação da API - Facebook Monitor

## Base URL

Por padrão, a aplicação roda em:
```
https://facebook-post-monitor.onrender.com
```
---

## Autenticação

Para usar os endpoints protegidos (posts e webhook), é necessário criar usuário e obter um token JWT:

### 1. Registro de usuário

**POST** `/register`

- Form data (application/x-www-form-urlencoded):
  - `username` (email)
  - `password`
- Resposta 201 Created:
  ```json
  { "msg": "User registered", "user_id": 1 }
  ```
- Erro 400: email já cadastrado.

### 2. Login

**POST** `/login`

- Form data (application/x-www-form-urlencoded):
  - `username` (email)
  - `password`
- Resposta 200 OK:
  ```json
  { "access_token": "<JWT>", "token_type": "bearer" }
  ```
- Erro 400: credenciais incorretas.

**Uso do token:** inclua o header HTTP:
```
Authorization: Bearer <access_token>
```

---

## Endpoints

### 1. Adicionar post para monitoramento

**POST** `/posts`

- Descrição: Valida e adiciona um post ativo do Facebook à lista de monitoramento.
- Cabeçalhos:
  - `Authorization: Bearer <token>`
- Request Body (JSON):
  ```json
  {
    "url": "https://www.facebook.com/{page_id}/posts/{post_id}/"
  }
  ```
- Códigos de resposta:
  - 201 Created: Post válido e adicionado.
    ```json
    {
      "url": "https://..."
    }
    ```
  - 400 Bad Request: URL válida, mas post está inativo ou não existe.
  - 409 Conflict: URL já está na lista de monitoramento.
  - 422 Unprocessable Entity: URL não segue o formato esperado.

---

### 2. Listar posts monitorados

**GET** `/posts`

- Descrição: Retorna todas as URLs de posts que estão sendo monitorados.
- Cabeçalhos:
  - `Authorization: Bearer <token>`
- Resposta (200 OK):
  ```json
  {
    "posts": [
      "https://www.facebook.com/.../posts/.../",
      "https://..."
    ]
  }
  ```

---

### 3. Configurar Webhook

**POST** `/config/webhook`

- Descrição: Define a URL de callback para notificações quando um post ativo se torna inativo.
- Cabeçalhos:
  - `Authorization: Bearer <token>`
- Request Body (JSON):
  ```json
  {
    "url": "https://meu-servico.com/webhook"
  }
  ```
- Resposta (200 OK):
  ```json
  {
    "webhook": "https://meu-servico.com/webhook"
  }
  ```

---

### 4. Consultar Webhook

**GET** `/config/webhook`

- Descrição: Retorna a URL de webhook configurada.
- Cabeçalhos:
  - `Authorization: Bearer <token>`
- Resposta (200 OK):
  ```json
  {
    "webhook": "https://meu-servico.com/webhook"
  }
  ```
- Erro 404 Not Found: Webhook ainda não foi configurado.

---

## Monitoramento e Notificações

- A cada **5 minutos**, um job interno revalida todos os posts ativos.
- Quando um post deixa de ser ativo, ele é removido da lista e uma requisição **POST** é enviada para a URL configurada no webhook com o payload:
  ```json
  {
    "url": "https://www.facebook.com/.../posts/.../",
    "status": "inactive"
  }
  ```

---

## Exemplos de Uso

1. Registro de usuário:
   ```bash
   curl -X POST https://facebook-post-monitor.onrender.com/register \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=meuemail@example.com&password=minhasenha"
   ```

2. Login:
   ```bash
   curl -X POST https://facebook-post-monitor.onrender.com/login \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=meuemail@example.com&password=minhasenha"
   ```

3. Adicionar post:
   ```bash
   curl -X POST https://facebook-post-monitor.onrender.com/posts \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <access_token>" \
     -d '{"url":"https://www.facebook.com/61576190405241/posts/122102364680873013/"}'
   ```

4. Listar posts:
   ```bash
   curl https://facebook-post-monitor.onrender.com/posts \
     -H "Authorization: Bearer <access_token>"
   ```

5. Configurar webhook:
   ```bash
   curl -X POST https://facebook-post-monitor.onrender.com/config/webhook \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <access_token>" \
     -d '{"url":"https://meu-servico.com/webhook"}'
   ```

6. Receber notificação (exemplo de payload recebido no seu endpoint):
   ```json
   {
     "url": "https://www.facebook.com/.../posts/.../",
     "status": "inactive"
   }
   ```
