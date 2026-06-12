"""Owner registration and persistence.

The first user to /start becomes the owner. Their Telegram id is stored
locally so Hermes only ever responds to them.
"""
import json
import os
from typing import Optional


class Owner:
    def __init__(self, path: str):
        self._path = path
        self._owner_id: Optional[int] = self._load()

    def _load(self) -> Optional[int]:
        if not os.path.exists(self._path):
            return None
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return int(data["owner_id"])
        except (ValueError, KeyError, OSError):
            return None

    def is_set(self) -> bool:
        return self._owner_id is not None

    def is_owner(self, user_id: int) -> bool:
        return self._owner_id is not None and user_id == self._owner_id

    def register(self, user_id: int) -> None:
        self._owner_id = int(user_id)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump({"owner_id": self._owner_id}, f)
