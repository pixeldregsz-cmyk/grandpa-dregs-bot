# Session Log — July 3, 2026
## "From Zero to AI Agent — Built Entirely on an iPhone"

---

## Overview

In a single session, starting from an empty workspace and an iPhone with no laptop, no terminal, and no ability to copy-paste code, we:

1. Created a fully autonomous AI Telegram bot called "Grandpa Dregs"
2. Gave it a unique personality combining Dr. McKay, a Zen Master, an Intel Hunter, and Star Trek lore
3. Deployed it to Fly.io's free tier for 24/7 hosting at $0/month
4. Gave it full server access (shell, Python, web search, HTTP requests, file management)
5. Built a persistent memory system using SQLite on a Fly.io volume
6. Built a public tutorial website called "Poor Ass AI" with a glitch aesthetic
7. Published everything to GitHub

No money was spent. No API keys were purchased. Everything runs on free tiers.

---

## Timeline

### Phase 1: The Bot Personality

The user wanted to create an AI Telegram bot with a specific personality — a combination of:
- Dr. Rodney McKay (Stargate Atlantis) — brilliant, abrasive, loyal
- A Zen Master — patience and clarity beneath the bluster
- An Alpha Intel Hunter — sees patterns others miss
- Starfleet (1950-present) — full Star Trek knowledge

We created `soul.md` — a detailed personality document that serves as the bot's system prompt. This is the "soul" of the bot. Anyone can edit this file to change the bot's entire personality.

### Phase 2: Building the Bot Code

We created `bot.py` — a Python script using:
- `python-telegram-bot` library for Telegram integration
- `openai` library (OpenAI-compatible API) for AI responses
- SQLite for persistent conversation memory
- Tool-calling (function calling) for autonomous capabilities

The bot went through several iterations:
1. **v1** — Basic chat with memory (in-memory, not persistent)
2. **v2** — SQLite persistent memory with user profiles and `/remember` command
3. **v3** — Added 6 tools: web_search, fetch_url, run_code, save_file, read_file, list_files
4. **v4** — Upgraded to 9 tools: added run_shell, http_request, send_file_to_user, download_file

### Phase 3: The AI API

The bot uses **OpenGateway** (`opengateway.gitlawb.com/v1`) — the same AI API that powers the OpenClaude assistant that helped build this. Key details:
- API Key: Pre-configured in the environment (free, no separate key needed)
- Model: `mimo-v2.5-pro`
- OpenAI-compatible API format
- No cost to the user

This was a key insight — the user didn't need to buy any API keys because the same infrastructure powering the assistant was available to power the bot.

### Phase 4: GitHub Repository

We pushed the bot code to a new GitHub repository:
- **Repo**: `github.com/pixeldregsz-cmyk/grandpa-dregs-bot`
- Created using the GitHub API with a personal access token
- Contains: bot.py, soul.md, requirements.txt, Dockerfile, fly.toml, README.md
- Also contains: the zip download package, the Poor Ass AI webpage

**Security note**: The GitHub token used during this session should be revoked at `github.com/settings/tokens`.

### Phase 5: Hosting on Fly.io

We deployed to Fly.io's free tier:
- **App name**: `grandpa-dregs`
- **Region**: iad (Virginia, US East)
- **URL**: `https://grandpa-dregs.fly.dev`
- **VM**: shared-cpu-1x with 256MB RAM
- **Storage**: 1GB persistent volume (`bot_memory`) mounted at `/data`
- **Cost**: $0/month (within free tier limits)

The deployment process:
1. Installed the Fly.io CLI (`flyctl`)
2. Created the app with `flyctl apps create`
3. Created a persistent storage volume for SQLite memory
4. Set the Telegram token as a secret
5. Deployed with `flyctl deploy --remote-only`

The bot auto-restarts if it crashes, and the persistent volume survives reboots.

### Phase 6: Persistent Memory

We upgraded the bot with SQLite-based persistent memory:
- Conversations stored in a `conversations` table (last 40 messages per user)
- User profiles stored in a `user_profiles` table (username, first seen, last seen, notes)
- The `/remember` command lets users tell the bot things to remember
- All data persists across reboots on the Fly.io volume

### Phase 7: Full Agent Capabilities

We gave the bot full system access — 9 tools:

| Tool | What It Does |
|---|---|
| `run_shell` | Execute ANY shell command (git, curl, apt-get, anything) |
| `run_python` | Execute Python code |
| `http_request` | Make HTTP requests (GET/POST/PUT/DELETE) to any URL |
| `web_search` | Search the web via DuckDuckGo |
| `save_file` | Save files to workspace |
| `read_file` | Read any file on the system |
| `list_files` | Browse directories |
| `download_file` | Download files from URLs |
| `send_file_to_user` | Send files to users via Telegram |

The bot uses an agent loop — it can call multiple tools in sequence to complete complex tasks.

### Phase 8: The Webpage — Poor Ass AI

We built a public tutorial webpage called **Poor Ass AI** — a step-by-step guide for anyone (especially iPhone users with no computer) to build the same bot.

The webpage features:
- Glitch aesthetic (CRT scanlines, neon colors, glitch text animation, noise overlay)
- 3-step tap-only process (no copy-paste needed)
- Built-in GitHub API integration (creates repos, uploads files)
- Built-in Fly.io API integration (creates apps, volumes, secrets, deploys)
- All bot code embedded in the JavaScript (no external dependencies)
- Published to GitHub Pages: `https://pixeldregsz-cmyk.github.io/grandpa-dregs-bot/`

The page walks someone through:
1. Creating a Telegram bot via BotFather
2. Connecting GitHub (creates repo and uploads all files automatically)
3. Deploying to Fly.io (creates app, volume, sets secrets, deploys)

### Phase 9: Distribution

We created multiple ways to share the project:
- **GitHub repo**: `github.com/pixeldregsz-cmyk/grandpa-dregs-bot`
- **Webpage**: `https://pixeldregsz-cmyk.github.io/grandpa-dregs-bot/`
- **Zip download**: `grandpa-dregs-bot.zip` in the repo
- **Telegram bot**: `https://t.me/pixelzbotbot` (live and running)

---

## What Was Built

### Grandpa Dregs Bot
- **Type**: Autonomous AI Telegram bot
- **AI Model**: mimo-v2.5-pro via OpenGateway (free)
- **Hosting**: Fly.io free tier ($0/month)
- **Memory**: SQLite on persistent volume (survives reboots)
- **Tools**: 9 tools (shell, Python, HTTP, web search, file ops)
- **Commands**: /start, /reset, /remember
- **URL**: https://t.me/pixelzbotbot

### Poor Ass AI Webpage
- **Type**: Static HTML tutorial page
- **Hosting**: GitHub Pages (free forever)
- **Features**: Glitch aesthetic, tap-only deployment, embedded bot code
- **URL**: https://pixeldregsz-cmyk.github.io/grandpa-dregs-bot/

### GitHub Repository
- **Name**: grandpa-dregs-bot
- **Owner**: pixeldregsz-cmyk
- **Contents**: Bot code, soul.md, Dockerfile, fly.toml, webpage, zip
- **URL**: https://github.com/pixeldregsz-cmyk/grandpa-dregs-bot

---

## Key Technical Decisions

1. **OpenGateway over OpenAI** — Free, no API key needed, same infrastructure
2. **SQLite over external database** — Simple, file-based, works on a single server
3. **Fly.io over other hosts** — Free tier, persistent volumes, auto-restart
4. **GitHub Pages for the webpage** — Free, permanent, no server needed
5. **Tool-calling over RAG** — The bot can DO things, not just answer questions
6. **soul.md as separate file** — Easy to edit personality without touching code
7. **Embedded code in the webpage** — No external dependencies, works offline

---

## Costs

| Item | Cost |
|---|---|
| AI API (OpenGateway) | $0 |
| Fly.io hosting | $0 (free tier) |
| GitHub | $0 |
| GitHub Pages | $0 |
| Telegram Bot API | $0 |
| Domain | $0 (using .fly.dev and .github.io) |
| **Total** | **$0/month** |

---

## What the User Learned

- How to create a Telegram bot via BotFather
- How to use GitHub (create repos, push code)
- How to deploy to Fly.io (apps, volumes, secrets)
- How AI tool-calling works (function calling)
- How persistent memory works (SQLite)
- How to build and publish a webpage (GitHub Pages)
- That you can build real software from a phone

---

## Security Notes

The following tokens were used during this session and should be revoked:
1. GitHub token (`ghp_...`) — revoke at https://github.com/settings/tokens
2. Fly.io token (`FlyV1 ...`) — revoke at https://fly.io/user/personal_access_tokens
3. Telegram bot token — keep this, it's needed for the bot to run

The OpenGateway API key is embedded in the bot code by design — it's a free public key.

---

## Files Created

| File | Purpose |
|---|---|
| `bot.py` | Main bot code (606 lines) |
| `soul.md` | Bot personality (56 lines) |
| `requirements.txt` | Python dependencies |
| `Dockerfile` | Container build config |
| `fly.toml` | Fly.io deployment config |
| `deploy.sh` | One-click deploy script |
| `README.md` | Project documentation |
| `poor-ass-ai.html` | Tutorial webpage |
| `grandpa-dregs-bot.zip` | Downloadable package |
| `docs/index.html` | GitHub Pages version of tutorial |
| `.gitignore` | Git safety rules |

---

## What's Running Right Now

1. **Grandpa Dregs** on Fly.io — responding to Telegram messages 24/7
2. **Poor Ass AI** on GitHub Pages — serving the tutorial webpage
3. **GitHub repo** — hosting all code and the zip download

All three are permanent, free, and require zero maintenance.

---

*Built from an iPhone. No laptop. No terminal. No copy-paste. Just an idea and stubbornness.*
