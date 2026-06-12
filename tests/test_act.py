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
    # Use the raw record: pytest's caplog.text strips ANSI escape sequences.
    logged = caplog.records[-1].getMessage()
    # Tag present and only the intent value is wrapped in the blue ANSI codes.
    assert logged.startswith("[intent]")
    assert "\033[94mquestion about scheduling\033[0m" in logged


def test_assistant_action_handles_claude_error():
    class Boom:
        def respond(self, history, text):
            raise RuntimeError("api down")

    action = AssistantAction(Boom())
    msg = build_understood(owner_id=1, text="hi", history=[])
    reply = asyncio.run(action.act(msg))
    assert "error" in reply.lower()
