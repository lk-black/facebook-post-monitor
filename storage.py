import os
import sqlite3
import threading

class PostStorage:
    """
    Armazena URLs de posts ativos em banco SQLite thread-safe.
    Suporta múltiplos usuários.
    """
    def __init__(self, db_path: str = None):
        self._lock = threading.Lock()
        if db_path is None:
            db_path = os.getenv("STORAGE_DB_PATH", "posts.db")
        # permite uso em múltiplas threads
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        # Migration: ensure posts table has user_id column; if not, drop and recreate
        cur = self._conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='posts'")
        if cur.fetchone():
            info = self._conn.execute("PRAGMA table_info(posts)").fetchall()
            cols = [row[1] for row in info]
            if 'user_id' not in cols:
                # Drop legacy posts table and recreate new schema
                self._conn.execute("DROP TABLE posts")
        # Tabelas para multi-usuário
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, password_hash TEXT)"
        )
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS posts (user_id INTEGER, url TEXT, PRIMARY KEY(user_id,url))"
        )
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS webhooks (user_id INTEGER PRIMARY KEY, url TEXT)"
        )
        self._conn.commit()

    def register_user(self, email: str, password_hash: str) -> int:
        """
        Registra um novo usuário.
        """
        with self._lock:
            cur = self._conn.execute(
                "INSERT INTO users(email, password_hash) VALUES(?,?)",
                (email, password_hash)
            )
            self._conn.commit()
            return cur.lastrowid

    def get_user(self, email: str):
        """
        Retorna informações do usuário pelo email.
        """
        with self._lock:
            cur = self._conn.execute(
                "SELECT id, email, password_hash FROM users WHERE email = ?", (email,)
            )
            row = cur.fetchone()
            return row and {"id": row[0], "email": row[1], "password_hash": row[2]}

    def add(self, post_url: str, user_id: int) -> bool:
        """
        Adiciona um post para o usuário.
        """
        with self._lock:
            try:
                self._conn.execute(
                    "INSERT INTO posts(user_id, url) VALUES(?,?)", (user_id, post_url)
                )
                self._conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def remove(self, post_url: str, user_id: int) -> bool:
        """
        Remove um post do usuário.
        """
        with self._lock:
            cur = self._conn.execute(
                "DELETE FROM posts WHERE user_id = ? AND url = ?", (user_id, post_url)
            )
            self._conn.commit()
            return cur.rowcount > 0

    def list_user_posts(self, user_id: int):
        """
        Lista todos os posts de um usuário.
        """
        with self._lock:
            cur = self._conn.execute(
                "SELECT url FROM posts WHERE user_id = ?", (user_id,)
            )
            return [row[0] for row in cur.fetchall()]

    def list_all_posts(self):
        """
        Lista todos os posts de todos os usuários.
        """
        with self._lock:
            cur = self._conn.execute("SELECT user_id, url FROM posts")
            return cur.fetchall()  # list of (user_id, url)

    def set_webhook(self, user_id: int, url: str) -> None:
        """
        Armazena URL de webhook para notificações de um usuário.
        """
        with self._lock:
            self._conn.execute(
                "INSERT OR REPLACE INTO webhooks(user_id, url) VALUES(?,?)", (user_id, url)
            )
            self._conn.commit()

    def get_webhook(self, user_id: int) -> str | None:
        """
        Retorna URL de webhook configurada para um usuário ou None.
        """
        with self._lock:
            cur = self._conn.execute(
                "SELECT url FROM webhooks WHERE user_id = ?", (user_id,)
            )
            row = cur.fetchone()
            return row[0] if row else None
