import pytest

from hermes.config import load_config, ConfigError


@pytest.fixture(autouse=True)
def no_dotenv(monkeypatch):
    # Keep these tests hermetic: do not read the developer's real .env file,
    # only the environment variables each test sets explicitly.
    monkeypatch.setattr("hermes.config.load_dotenv", lambda *a, **k: None)


def test_load_config_reads_values(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "key")
    cfg = load_config()
    assert cfg.telegram_token == "tok"
    assert cfg.anthropic_api_key == "key"
    assert cfg.model == "claude-haiku-4-5-20251001"


def test_load_config_missing_token_raises(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "key")
    with pytest.raises(ConfigError) as exc:
        load_config()
    assert "TELEGRAM_BOT_TOKEN" in str(exc.value)


def test_load_config_missing_key_raises(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(ConfigError) as exc:
        load_config()
    assert "ANTHROPIC_API_KEY" in str(exc.value)
