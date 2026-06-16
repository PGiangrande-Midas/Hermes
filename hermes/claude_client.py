"""Anthropic wrapper. Returns a structured (intent, reply) for each message."""
from typing import Dict, List, Tuple

import anthropic
from metis import instrument

SYSTEM_PROMPT = (
    "You are Hermes, the owner's personal AI agent and messenger. You are "
    "sharp, concise, capable, and a little bit of a personality. You are an "
    "agent, not a chatbot: answer directly, do not pad, do not over-apologize.\n"
    "\n"
    "Format every response exactly like this: the first line is the literal "
    "text 'INTENT: ' followed by a short label, then a newline, then your "
    "reply to the user. Write that first line as plain text with no markdown, "
    "no bold, no quotes, and no extra punctuation, so it always starts with the "
    "seven characters 'INTENT:'.\n"
    "\n"
    "The label names what the user is clearly trying to do. Rules for it:\n"
    "- Always commit to a concrete best-guess label. Never write 'unknown', "
    "'unclear', or 'n/a'. Even a vague, short, or one-word message gets a "
    "meaningful label based on what the user is plainly doing.\n"
    "- Keep it 1 to 3 words, all lowercase.\n"
    "- Choose the closest fit, such as: greeting, small talk, identity "
    "question, capability question, clarification, question, request, or "
    "command.\n"
    "Examples: 'Hallo' -> greeting. 'How are you?' -> small talk. 'Who are "
    "you?' -> identity question. 'Are you an LLM or an agent?' -> capability "
    "question.\n"
    "\n"
    "The user never sees the INTENT line, so never refer to it. Do not use "
    "em-dashes or en-dashes anywhere; use plain hyphens or commas."
)

MAX_TOKENS = 1024
# Bound each request so a stalled connection fails fast instead of hanging for
# the SDK default of 600 seconds. One retry still covers a transient blip.
REQUEST_TIMEOUT = 30.0
MAX_RETRIES = 1


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
        if sdk is not None:
            self._client = sdk
        else:
            # Wrap the real client once so every messages.create feeds token
            # usage and per-model cost into the active Metis track() run.
            self._client = instrument(
                anthropic.AsyncAnthropic(
                    api_key=api_key,
                    timeout=REQUEST_TIMEOUT,
                    max_retries=MAX_RETRIES,
                )
            )
        self._model = model

    async def respond(
        self, history: List[Dict[str, str]], text: str
    ) -> Tuple[str, str]:
        messages = list(history) + [{"role": "user", "content": text}]
        message = await self._client.messages.create(
            model=self._model,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=messages,
        )
        return parse_intent_reply(message.content[0].text)
