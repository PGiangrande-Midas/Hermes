# Hermes Design Spec

Date: 2026-06-12
Status: Approved

## Concept

Hermes is a Telegram-based AI agent with his own bot identity. The owner
messages Hermes from anywhere; Hermes interprets the message via Claude and
responds autonomously in natural language. Persona: sharp, concise, capable,
a bit of personality fitting "the messenger" - an agent, not a chatbot.

This is Day 3 of a 30-day agent series. Hermes will later become the dispatcher
interface to a multi-agent system (PANTHEON). The architecture must separate two
concerns from day one:

1. UNDERSTAND - receive a message, interpret intent via Claude.
2. ACT - decide what to do and respond.

Today ACT is "respond intelligently as a helpful assistant." Later ACT routes to
other agents. The seam is built now so the upgrade is trivial.

## Stack

- Python 3.
- `python-telegram-bot` (async, long-polling via getUpdates). Built-in handlers,
  polling loop, and chat-action "typing" helper.
- `anthropic` SDK.
- `python-dotenv` for config.
- Model: `claude-haiku-4-5-20251001`.
- All dependencies pinned in `requirements.txt`.

Long polling only. No webhooks, no public URL, no tunnel. Hermes runs on Paul's
machine and polls Telegram.

## The Core Seam (UNDERSTAND -> ACT)

```
Telegram update
  -> handlers (transport: receive, owner-check, typing indicator, send reply)
       -> understand  (build UnderstoodMessage: owner id, text, history, intent slot)
            -> act     (pluggable action layer -> returns reply string)
```

- `understand` turns a raw Telegram message into an `UnderstoodMessage`
  (owner id, text, recent conversation history, and a structured `intent` field).
- `act` exposes one function: `async def act(msg: UnderstoodMessage) -> str`.
  Today its only implementation, `AssistantAction`, calls Claude and returns a
  natural reply. Later, `DispatcherAction` swaps in to route on `msg.intent` to
  PANTHEON agents. Handlers never know which implementation they are talking to.
  That indirection is the seam.

### Structured intent from day one

The single Claude call returns a structured result: a one-line `intent` label and
the `reply` text. `AssistantAction` logs the intent to the console (not to the
user), for example:

```
[intent] question about scheduling
```

The user only ever sees `reply`. Producing a structured intent now forces the
understand layer to emit exactly the signal `DispatcherAction` will route on
later, making the PANTHEON upgrade path real rather than theoretical, at near-zero
cost today.

## Components

- `config.py` - load `.env`, validate `TELEGRAM_BOT_TOKEN` and `ANTHROPIC_API_KEY`
  are present (fail fast with a clear message otherwise), hold constants
  (model id, history cap, file paths).
- `owner.py` - owner registration and persistence to gitignored `owner.json`.
  First `/start` records the sender id. Afterwards every update is checked against
  it; non-owners are ignored silently.
- `memory.py` - conversation store backed by gitignored `conversation.json`.
  A list of `{role, content}` capped at the last N turns. Loaded at startup,
  written after each turn. `/reset` clears it.
- `claude_client.py` - wraps the Anthropic call with Hermes's system prompt and
  returns the structured `{intent, reply}` result.
- `understand.py` - defines `UnderstoodMessage` and builds it from an update plus
  current history.
- `act.py` - the action layer. `Action` interface plus `AssistantAction`
  (calls Claude, logs intent, returns reply).
- `bot.py` - wires handlers and runs polling. Entry point.

## Behavior

- `/start` - register owner if unset, then greet and give a brief self-intro.
- `/reset` - clear conversation history, confirm to the owner.
- Normal text - owner-check, send `typing` chat action, understand, act, reply.
  Append both the user message and Hermes's reply to history.

## Data and Persistence

- `owner.json`: `{"owner_id": <int>}`. Gitignored (personal Telegram id).
- `conversation.json`: list of `{role, content}` turns, capped. Gitignored.
- Both loaded at startup, written after each relevant turn.

## Error Handling

- Missing env vars: fail fast at startup with a clear message naming the missing
  variable.
- Claude API errors: caught inside `AssistantAction`, turned into a graceful
  reply ("I hit an error reaching my brain, try again") rather than crashing the
  poll loop. Logged to console.
- Non-owner messages: dropped silently.
- The polling loop must survive per-message errors.

## Testing

- `owner`: register-on-first-start, ignore non-owners, persistence round-trip.
- `memory`: append, cap at N, reset, persistence round-trip.
- `act`: `AssistantAction` with a mocked Claude client - asserts reply returned
  and intent logged.
- `claude_client`: structured result parsing with a mocked SDK response.
- Transport/polling stays thin so it needs no live Telegram connection.

## Security

- `.gitignore` committed first, listing `.env`, `owner.json`, `conversation.json`,
  `__pycache__/`, `venv/`, `*.pyc`.
- `.env` and `.env.example` both present with empty values only. No real secrets.
- `.env.example` structure:

  ```
  # Telegram Bot Token from BotFather
  TELEGRAM_BOT_TOKEN=
  # Anthropic API key -> https://console.anthropic.com/settings/keys
  ANTHROPIC_API_KEY=
  ```

- No hardcoded tokens or keys anywhere.

## Constraints

- No em-dashes or en-dashes anywhere in code, comments, or output text.
  Use hyphens, commas, or rephrase.
- Dependencies pinned.

## Deliverable

Paul fills in `.env`, runs one command, opens Telegram, messages Hermes, and gets
intelligent autonomous replies. The understand/act seam, including structured
intent, is in place for future PANTHEON dispatch.
