"""The UNDERSTAND layer: turn a raw message into a structured UnderstoodMessage.

Today this is light. Later it grows into real intent interpretation that the
DispatcherAction routes on. The `intent` field is populated by the action layer
after Claude returns, so the seam already carries the routing signal.
"""
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class UnderstoodMessage:
    owner_id: int
    text: str
    history: List[Dict[str, str]] = field(default_factory=list)
    intent: str = ""


def build_understood(
    owner_id: int, text: str, history: List[Dict[str, str]]
) -> UnderstoodMessage:
    return UnderstoodMessage(
        owner_id=owner_id, text=text, history=list(history)
    )
