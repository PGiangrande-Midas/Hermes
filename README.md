# Hermes

Your personal AI agent on Telegram. Message Hermes from anywhere; he interprets
what you want via Claude and replies autonomously. Day 3 of a 30-day agent
series, built with a clean UNDERSTAND -> ACT seam for future multi-agent
dispatch (PANTHEON).

## Setup

1. Create a bot with [@BotFather](https://t.me/BotFather) and copy the token.
2. Get an Anthropic API key: https://console.anthropic.com/settings/keys
3. Copy `.env.example` to `.env` and fill in both values.
4. Install dependencies:

   ```
   python -m venv venv
   venv/Scripts/pip install -r requirements.txt
   ```

## Run

```
venv/Scripts/python -m hermes
```

Open Telegram, find your bot, send `/start`. The first person to `/start`
becomes the owner; Hermes ignores everyone else from then on.

## Commands

- `/start` - register as owner (first time) and get a greeting.
- `/reset` - clear the conversation history.
- Any message - Hermes interprets and replies.

## Architecture

Hermes separates two concerns so the system can grow into a dispatcher later:

- UNDERSTAND (`hermes/understand.py`) - turns a raw message into a structured
  `UnderstoodMessage` carrying the text, recent history, and an `intent` field.
- ACT (`hermes/act.py`) - a pluggable `Action`. Today `AssistantAction` calls
  Claude, logs the interpreted intent to the console, and returns a reply.
  Later a `DispatcherAction` with the same interface will route on the intent
  to other agents.

The Telegram transport (`hermes/bot.py`) only does owner-checking, the typing
indicator, and message passing. It never knows which action it is talking to.

## Tests

```
venv/Scripts/python -m pytest
```
