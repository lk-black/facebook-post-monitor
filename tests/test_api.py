import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from api import app, storage
from fb_api import get_facebook_post_status

# Override storage DB path to avoid interfering with prod DB
os.environ['STORAGE_DB_PATH'] = tempfile.NamedTemporaryFile(delete=False).name
storage = storage  # ensure using fresh storage instance

@pytest.fixture(autouse=True)
def clear_storage(monkeypatch):
    # Reset DB for each test
    storage._conn.execute("DELETE FROM users")
    storage._conn.execute("DELETE FROM posts")
    storage._conn.execute("DELETE FROM webhooks")
    storage._conn.commit()
    # Mock Facebook API status: active for any URL containing 'active', inactive otherwise
    monkeypatch.setattr('fb_api.get_facebook_post_status', lambda url: 'active' in url)
    return

client = TestClient(app)

def test_register_and_login():
    # Register user
    response = client.post('/register', data={'username': 'a@b.com', 'password': 'pass'})
    assert response.status_code == 201
    # Duplicate registration fails
    response2 = client.post('/register', data={'username': 'a@b.com', 'password': 'pass'})
    assert response2.status_code == 400
    # Login
    response3 = client.post('/login', data={'username': 'a@b.com', 'password': 'pass'})
    assert response3.status_code == 200
    token = response3.json()['access_token']
    # Wrong login
    response4 = client.post('/login', data={'username': 'a@b.com', 'password': 'wrong'})
    assert response4.status_code == 400

def test_post_and_list(monkeypatch):
    # Setup user and token
    client.post('/register', data={'username': 'u@x.com', 'password': 'pw'})
    login = client.post('/login', data={'username': 'u@x.com', 'password': 'pw'})
    token = login.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    # Add active and inactive
    r1 = client.post('/posts', json={'url': 'http://example.com/active'}, headers=headers)
    assert r1.status_code == 201
    r2 = client.post('/posts', json={'url': 'http://example.com/inactive'}, headers=headers)
    assert r2.status_code == 400
    # Duplicate
    r3 = client.post('/posts', json={'url': 'http://example.com/active'}, headers=headers)
    assert r3.status_code == 409
    # List
    r4 = client.get('/posts', headers=headers)
    assert r4.status_code == 200
    assert 'http://example.com/active' in r4.json()['posts']

def test_webhook_config(monkeypatch):
    client.post('/register', data={'username': 'w@x.com', 'password': 'pw'})
    token = client.post('/login', data={'username': 'w@x.com', 'password': 'pw'}).json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    # Set
    r1 = client.post('/config/webhook', json={'url': 'http://hook'}, headers=headers)
    assert r1.status_code == 200
    # Get
    r2 = client.get('/config/webhook', headers=headers)
    assert r2.status_code == 200
    assert r2.json()['webhook'] == 'http://hook'

def test_unauthorized():
    assert client.get('/posts').status_code == 401
    assert client.post('/posts', json={'url': 'http://active'}).status_code == 401
    assert client.post('/config/webhook', json={'url': 'http://hook'}).status_code == 401
