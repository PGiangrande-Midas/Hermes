"""Anthropic wrapper. Returns a structured (intent, reply) for each message."""
from typing import Dict, List, Tuple

import anthropic

SYSTEM_PROMPT = (
    "You are Hermes, the owner's personal AI agent and messenger. You are "
    "sharp, concise, capable, and a little bit of a personality. You are an "
    "agent, not a chatbot: answer directly, do not pad, do not over-apologize. "
    "Format every response exactly like this: the first line must be "
    "'INTENT: <a few words naming what the user wants>', then a newline, then "
    "your reply to the user. The user never sees the INTENT line, so never "
    "refer to it. Do not use em-dashes or en-dashes; use plain hyphens or "
    "commas."
)

MAX_TOKENS = 1024


def parse_intent_reply(text: str) -> Tuple[str, str]:
    stripped = text.lstrip()
    if stripped.upper().startswith("INTENT:"):
        first_newline = stripped.find("\n")
        if first_newline == -1:
            intent = stripped[len("INTENT:"):].strip()
            return (intent or "unknown", "")
        intent = stripped[len("INTENT:"):first_newline].strip()
        reply = stripped[first_newline + 1:].strip()
        return (intent or "unknown", reply)
    return ("unknown", text.strip())


class ClaudeClient:
    def __init__(self, api_key: str, model: str, sdk=None):
        self._client = sdk or anthropic.Anthropic(api_key=api_key)
        self._model = model

    def respond(
        self, history: List[Dict[str, str]], text: str
    ) -> Tuple[str, str]:
        messages = list(history) + [{"role": "user", "content": text}]
        message = self._client.messages.create(
            model=self._model,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=messages,
        )
        return parse_intent_reply(message.content[0].text)
