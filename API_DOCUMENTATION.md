# Documentação da API - Facebook Monitor

## Base URL

Por padrão, a aplicação roda em:

```
http://localhost:8000
```

A documentação interativa está disponível em:

```
http://localhost:8000/docs
```

---

## Endpoints

### 1. Adicionar post para monitoramento

**POST** `/posts`

- Descrição: Valida e adiciona um post ativo do Facebook à lista de monitoramento.
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

1. Adicionar post:
   ```bash
   curl -X POST http://localhost:8000/posts \
     -H "Content-Type: application/json" \
     -d '{"url":"https://www.facebook.com/61576190405241/posts/122102364680873013/"}'
   ```

2. Listar posts:
   ```bash
   curl http://localhost:8000/posts
   ```

3. Configurar webhook:
   ```bash
   curl -X POST http://localhost:8000/config/webhook \
     -H "Content-Type: application/json" \
     -d '{"url":"https://meu-servico.com/webhook"}'
   ```

4. Receber notificação (exemplo de payload recebido no seu endpoint):
   ```json
   {
     "url": "https://www.facebook.com/.../posts/.../",
     "status": "inactive"
   }
   ```
