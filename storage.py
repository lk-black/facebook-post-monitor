import os
import sqlite3
import threading

class PostStorage:
    """
    Armazena URLs de posts ativos em banco SQLite thread-safe.
    """
    def __init__(self, db_path: str = None):
        self._lock = threading.Lock()
        if db_path is None:
            db_path = os.getenv("STORAGE_DB_PATH", "posts.db")
        # permite uso em múltiplas threads
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS posts (url TEXT PRIMARY KEY)"
        )
        # tabela para configurações, ex: webhook
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT)"
        )
        self._conn.commit()

    def add(self, post_url: str) -> bool:
        with self._lock:
            try:
                self._conn.execute(
                    "INSERT INTO posts(url) VALUES(?)", (post_url,)
                )
                self._conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def remove(self, post_url: str) -> bool:
        with self._lock:
            cur = self._conn.execute(
                "DELETE FROM posts WHERE url = ?", (post_url,)
            )
            self._conn.commit()
            return cur.rowcount > 0

    def list_all(self):
        with self._lock:
            cur = self._conn.execute("SELECT url FROM posts")
            return [row[0] for row in cur.fetchall()]

    def set_webhook(self, url: str) -> None:
        """
        Armazena URL de webhook para notificações.
        """
        with self._lock:
            self._conn.execute(
                "INSERT OR REPLACE INTO config(key, value) VALUES(?, ?)",
                ("webhook_url", url)
            )
            self._conn.commit()

    def get_webhook(self) -> str | None:
        """
        Retorna URL de webhook configurada ou None.
        """
        with self._lock:
            cur = self._conn.execute(
                "SELECT value FROM config WHERE key = ?", ("webhook_url",)
            )
            row = cur.fetchone()
            return row[0] if row else None
