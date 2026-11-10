import secrets
import time
from dataclasses import dataclass


@dataclass
class _Entry:
    nonce: str
    expires_at: float


class NonceStore:
    def __init__(self, ttl: float = 300.0, nbytes: int = 16) -> None:
        self.ttl = ttl
        self.nbytes = nbytes
        self._by_chat: dict[int, _Entry] = {}

    def issue(self, chat_id: int) -> str:
        n = secrets.token_urlsafe(self.nbytes)
        self._by_chat[chat_id] = _Entry(nonce=n, expires_at=time.monotonic() + self.ttl)
        return n

    def peek(self, chat_id: int) -> str | None:
        e = self._by_chat.get(chat_id)
        if not e or e.expires_at < time.monotonic():
            self._by_chat.pop(chat_id, None)
            return None
        return e.nonce

    def consume(self, chat_id: int, nonce: str) -> bool:
        e = self._by_chat.get(chat_id)
        if not e:
            return False
        if e.expires_at < time.monotonic():
            self._by_chat.pop(chat_id, None)
            return False
        if not secrets.compare_digest(e.nonce, nonce):
            return False
        self._by_chat.pop(chat_id, None)
        return True

    def purge(self) -> int:
        now = time.monotonic()
        dead = [k for k, v in self._by_chat.items() if v.expires_at < now]
        for k in dead:
            self._by_chat.pop(k, None)
        return len(dead)
