"""Conversation history store, persisted to a local JSON file and capped."""
import json
import os
from typing import Dict, List


class Memory:
    def __init__(self, path: str, cap: int):
        self._path = path
        self._cap = cap
        self._turns: List[Dict[str, str]] = self._load()

    def _load(self) -> List[Dict[str, str]]:
        if not os.path.exists(self._path):
            return []
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data[-self._cap:]
        except (ValueError, OSError):
            pass
        return []

    def _save(self) -> None:
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._turns, f)

    def append(self, role: str, content: str) -> None:
        self._turns.append({"role": role, "content": content})
        if len(self._turns) > self._cap:
            self._turns = self._turns[-self._cap:]
        self._save()

    def history(self) -> List[Dict[str, str]]:
        return list(self._turns)

    def reset(self) -> None:
        self._turns = []
        self._save()
