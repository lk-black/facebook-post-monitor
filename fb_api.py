import os
from urllib.parse import urlparse
import requests

# Carrega token do ambiente (assume que load_dotenv() já foi chamado em main)
FACEBOOK_TOKEN = os.getenv("FACEBOOK_TOKEN")
GRAPH_API_BASE = "https://graph.facebook.com/v17.0"

def get_facebook_post_status(post_url: str) -> bool:
    """
    Recebe URL no formato
    https://www.facebook.com/{page_id}/posts/{post_id}/
    e retorna True se o post estiver ativo (status HTTP 200), False caso contrário.
    """
    parsed = urlparse(post_url)
    segments = parsed.path.strip("/").split("/")
    if len(segments) >= 3 and segments[1] == "posts":
        page_id, post_id = segments[0], segments[2]
    else:
        raise ValueError(f"URL inválida: {post_url}")

    graph_id = f"{page_id}_{post_id}"
    params = {
        "access_token": FACEBOOK_TOKEN,
        "fields": "id,message,created_time,story,permalink_url"
    }
    resp = requests.get(f"{GRAPH_API_BASE}/{graph_id}", params=params)
    return resp.status_code == 200
