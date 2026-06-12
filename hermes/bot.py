"""Transport layer: wire Telegram handlers to the understand -> act seam."""
import asyncio
import logging

import truststore

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from .act import AssistantAction
from .claude_client import ClaudeClient
from .config import load_config
from .memory import Memory
from .owner import Owner
from .understand import build_understood

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%H:%M:%S"
)
# Silence noisy third-party HTTP logging so Hermes's own activity feed is clean.
for _noisy in ("httpx", "httpcore", "telegram", "apscheduler"):
    logging.getLogger(_noisy).setLevel(logging.WARNING)
logger = logging.getLogger("hermes")

GREETING = (
    "Hermes here. I am your agent. Message me anything and I will handle it, "
    "answer it, or think it through with you. Short and sharp is my style."
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    owner: Owner = context.application.bot_data["owner"]
    if not owner.is_set():
        owner.register(user_id)
        logger.info("Registered owner: %s", user_id)
    if not owner.is_owner(user_id):
        return
    await update.message.reply_text(GREETING)


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    owner: Owner = context.application.bot_data["owner"]
    if not owner.is_owner(update.effective_user.id):
        return
    memory: Memory = context.application.bot_data["memory"]
    memory.reset()
    await update.message.reply_text("Conversation cleared. Fresh start.")


async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    owner: Owner = context.application.bot_data["owner"]
    user_id = update.effective_user.id
    if not owner.is_owner(user_id):
        return

    logger.info("[received]  message from owner")

    memory: Memory = context.application.bot_data["memory"]
    action: AssistantAction = context.application.bot_data["action"]
    text = update.message.text

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action=ChatAction.TYPING
    )

    msg = build_understood(
        owner_id=user_id, text=text, history=memory.history()
    )
    reply = await action.act(msg)

    memory.append("user", text)
    memory.append("assistant", reply)
    await update.message.reply_text(reply)
    logger.info("[reply]     sent")


def build_application() -> Application:
    cfg = load_config()
    owner = Owner(cfg.owner_file)
    memory = Memory(cfg.conversation_file, cfg.history_cap)
    claude = ClaudeClient(api_key=cfg.anthropic_api_key, model=cfg.model)
    action = AssistantAction(claude)

    app = Application.builder().token(cfg.telegram_token).build()
    app.bot_data["owner"] = owner
    app.bot_data["memory"] = memory
    app.bot_data["action"] = action

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))
    return app


def main() -> None:
    # Use the OS (Windows) certificate store for TLS verification. This trusts
    # any corporate proxy or antivirus root CA, which the bundled certifi store
    # does not. Covers both the Telegram and Anthropic connections.
    truststore.inject_into_ssl()
    # Python 3.14 no longer auto-creates an event loop in the main thread, so
    # ensure one exists before run_polling, which expects asyncio.get_event_loop
    # to succeed.
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
    app = build_application()
    logger.info("hermes online, polling")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
