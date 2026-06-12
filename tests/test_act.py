import asyncio
import logging

from hermes.act import AssistantAction
from hermes.understand import build_understood


class FakeClaude:
    def __init__(self, result=("greeting", "Hello there.")):
        self.result = result
        self.calls = []

    def respond(self, history, text):
        self.calls.append((history, text))
        return self.result


def test_assistant_action_returns_reply():
    action = AssistantAction(FakeClaude())
    msg = build_understood(owner_id=1, text="hi", history=[])
    reply = asyncio.run(action.act(msg))
    assert reply == "Hello there."


def test_assistant_action_sets_and_logs_intent(caplog):
    action = AssistantAction(FakeClaude(("question about scheduling", "Soon.")))
    msg = build_understood(owner_id=1, text="when?", history=[])
    with caplog.at_level(logging.INFO):
        asyncio.run(action.act(msg))
    assert msg.intent == "question about scheduling"
    assert "intent     question about scheduling" in caplog.text


def test_assistant_action_handles_claude_error():
    class Boom:
        def respond(self, history, text):
            raise RuntimeError("api down")

    action = AssistantAction(Boom())
    msg = build_understood(owner_id=1, text="hi", history=[])
    reply = asyncio.run(action.act(msg))
    assert "error" in reply.lower()
