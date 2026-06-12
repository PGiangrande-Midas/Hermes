"""Load and validate Hermes configuration from the environment."""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

MODEL = "claude-haiku-4-5-20251001"
HISTORY_CAP = 20  # max conversation turns kept (user + assistant entries)
OWNER_FILE = "owner.json"
CONVERSATION_FILE = "conversation.json"


class ConfigError(Exception):
    """Raised when required configuration is missing."""


@dataclass
class Config:
    telegram_token: str
    anthropic_api_key: str
    model: str = MODEL
    history_cap: int = HISTORY_CAP
    owner_file: str = OWNER_FILE
    conversation_file: str = CONVERSATION_FILE


def load_config() -> Config:
    load_dotenv()
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not token:
        raise ConfigError(
            "TELEGRAM_BOT_TOKEN is not set. Add it to your .env file."
        )
    if not key:
        raise ConfigError(
            "ANTHROPIC_API_KEY is not set. Add it to your .env file."
        )
    return Config(telegram_token=token, anthropic_api_key=key)
