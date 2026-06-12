import asyncio
import logging

from hermes import act as act_module
from hermes.act import AssistantAction, ERROR_REPLY
from hermes.understand import build_understood


class FakeClaude:
    def __init__(self, result=("greeting", "Hello there.")):
        self.result = result
        self.calls = []

    async def respond(self, history, text):
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
        async def respond(self, history, text):
            raise RuntimeError("api down")

    action = AssistantAction(Boom())
    msg = build_understood(owner_id=1, text="hi", history=[])
    reply = asyncio.run(action.act(msg))
    assert reply == ERROR_REPLY


def test_assistant_action_times_out_instead_of_hanging(monkeypatch):
    # A stalled Claude call must not hang the handler: it is bounded by the
    # CALL_TIMEOUT_SECONDS cap and falls back to ERROR_REPLY.
    monkeypatch.setattr(act_module, "CALL_TIMEOUT_SECONDS", 0.05)

    class Slow:
        async def respond(self, history, text):
            await asyncio.sleep(5)
            return ("x", "y")

    action = AssistantAction(Slow())
    msg = build_understood(owner_id=1, text="hi", history=[])
    reply = asyncio.run(action.act(msg))
    assert reply == ERROR_REPLY
