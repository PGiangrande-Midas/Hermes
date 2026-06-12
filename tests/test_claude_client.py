import asyncio
from unittest.mock import AsyncMock, MagicMock

from hermes.claude_client import ClaudeClient, parse_intent_reply


def test_parse_intent_reply_extracts_both():
    text = "INTENT: question about scheduling\nHere is your answer."
    intent, reply = parse_intent_reply(text)
    assert intent == "question about scheduling"
    assert reply == "Here is your answer."


def test_parse_intent_reply_missing_marker():
    intent, reply = parse_intent_reply("Just a reply with no marker.")
    assert intent == "unknown"
    assert reply == "Just a reply with no marker."


def test_respond_calls_sdk_and_parses():
    fake_block = MagicMock()
    fake_block.text = "INTENT: greeting\nHello there."
    fake_message = MagicMock()
    fake_message.content = [fake_block]
    fake_sdk = MagicMock()
    fake_sdk.messages.create = AsyncMock(return_value=fake_message)

    client = ClaudeClient(api_key="x", model="m", sdk=fake_sdk)
    intent, reply = asyncio.run(
        client.respond(history=[{"role": "user", "content": "hi"}], text="hi")
    )

    assert intent == "greeting"
    assert reply == "Hello there."
    assert fake_sdk.messages.create.called
