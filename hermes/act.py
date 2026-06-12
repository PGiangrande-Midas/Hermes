"""The ACT layer: a pluggable action that turns an UnderstoodMessage into a reply.

Today the only implementation is AssistantAction, which calls Claude and replies
as a helpful agent. Later, a DispatcherAction with the same interface will route
on msg.intent to PANTHEON agents. Handlers depend only on the Action interface.
"""
import asyncio
import logging
from abc import ABC, abstractmethod

from .understand import UnderstoodMessage

logger = logging.getLogger("hermes")

ERROR_REPLY = "I hit an error reaching my brain. Try again in a moment."


class Action(ABC):
    @abstractmethod
    async def act(self, msg: UnderstoodMessage) -> str:
        ...


class AssistantAction(Action):
    def __init__(self, claude_client):
        self._claude = claude_client

    async def act(self, msg: UnderstoodMessage) -> str:
        try:
            intent, reply = await asyncio.to_thread(
                self._claude.respond, msg.history, msg.text
            )
        except Exception as exc:  # keep the poll loop alive
            logger.error("Claude call failed: %s", exc)
            return ERROR_REPLY
        msg.intent = intent
        logger.info("intent     %s", intent.lower())
        return reply
