# Facebook Monitor

Aplicação Python para monitorar posts do Facebook via Graph API e notificar quando um post ativo se torna inativo.

## Recursos

- Adiciona e valida URLs de posts do Facebook.
- Armazena posts ativos em banco SQLite.
- Agendamento automático (APScheduler) para revalidar status a cada 5 minutos.
- Endpoints HTTP via FastAPI:
  - `POST /posts`  
  - `GET /posts`  
  - `POST /config/webhook`  
  - `GET /config/webhook`
- Suporte a webhook: dispara notificação HTTP quando um post vira inativo.
- Dockerfile para fácil deploy.

## Pré-requisitos

- Python 3.10+
- Facebook Graph API token
- Git
- Docker (opcional)

## Instalação local

1. Clone este repositório:
   ```bash
   git clone https://github.com/seu-usuario/facebook-monitor.git
   cd facebook-monitor
   ```
2. Crie um ambiente virtual e instale dependências:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. Crie um arquivo `.env` na raiz com as variáveis:
   ```ini
   FACEBOOK_TOKEN=<seu-token>
   STORAGE_DB_PATH=posts.db
   WEBHOOK_URL=<url-do-seu-webhook>
   PORT=8000
   ```
4. Inicie a aplicação:
   ```bash
   python main.py
   ```
5. Acesse http://localhost:8000/docs para ver a documentação interativa (Swagger UI).

## Endpoints

| Método | Rota                   | Descrição                                         |
| ------ | ---------------------- | ------------------------------------------------- |
| POST   | `/posts`               | Adiciona um post ativo à monitoração.             |
| GET    | `/posts`               | Lista todos os posts monitorados.                 |
| POST   | `/config/webhook`      | Configura URL de webhook para notificações.       |
| GET    | `/config/webhook`      | Retorna webhook configurado.                      |

### Exemplo de requisição `POST /posts`
```json
{
  "url": "https://www.facebook.com/<page>/posts/<post>/"
}
```

## Docker

Para build e rodar via Docker:
```bash
# build da imagem
docker build -t facebook-monitor .

# executa o container (mapeia porta 8000)
docker run -d \
  -p 8000:8000 \
  --env FACEBOOK_TOKEN=$FACEBOOK_TOKEN \
  --env WEBHOOK_URL=$WEBHOOK_URL \
  --env STORAGE_DB_PATH=/data/posts.db \
  -v $(pwd)/data:/data \
  facebook-monitor
```

## CI/CD

- GitHub Actions:
  - Lintagem (flake8/mypy)
  - Testes unitários com pytest
  - Build e push de imagem Docker

## Observabilidade

- Logs estruturados (padrão ISO timestamp).
- Níveis de log configuráveis via variável `LOG_LEVEL`.

## Licença

MIT © Seu Nome
