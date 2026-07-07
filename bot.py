#!/usr/bin/env python3
"""Grandpa Dregs Telegram Bot — OpenAI-compatible endpoint + soul.md personality."""

import os
import re
import json
import logging
import sqlite3
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime, timezone
from openai import OpenAI
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# --- Config ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.groq.com/openai/v1")
MODEL = os.environ.get("MODEL", "llama-3.3-70b-versatile")
SOUL_PATH = Path(__file__).parent / "soul.md"

# --- Logging ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# --- Load soul ---
SYSTEM_PROMPT = SOUL_PATH.read_text() if SOUL_PATH.exists() else "You are Grandpa Dregs."

# --- OpenAI-compatible client ---
client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

# --- Conversation memory (SQLite) ---
MAX_HISTORY = 20
DB_PATH = Path(os.environ.get("DB_PATH", "/tmp/grandpa-dregs/memory.db"))


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        "CREATE TABLE IF NOT EXISTS conversations (id INTEGER PRIMARY KEY AUTOINCREMENT,chat_id INTEGER NOT NULL,role TEXT NOT NULL,content TEXT NOT NULL,timestamp TEXT NOT NULL)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS user_profiles (chat_id INTEGER PRIMARY KEY,username TEXT,first_seen TEXT,last_seen TEXT,notes TEXT)"
    )
    conn.commit()
    conn.close()


def get_history(chat_id: int):
    conn = sqlite3.connect(str(DB_PATH))
    rows = conn.execute(
        "SELECT role,content FROM conversations WHERE chat_id=? ORDER BY id DESC LIMIT ?",
        (chat_id, MAX_HISTORY),
    ).fetchall()
    conn.close()
    return [{"role": r, "content": c} for r, c in reversed(rows)]


def add_message(chat_id: int, role: str, content: str):
    conn = sqlite3.connect(str(DB_PATH))
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO conversations (chat_id,role,content,timestamp) VALUES(?,?,?,?)",
        (chat_id, role, content, now),
    )
    conn.execute(
        "DELETE FROM conversations WHERE chat_id=? AND id NOT IN(SELECT id FROM conversations WHERE chat_id=? ORDER BY id DESC LIMIT ?)",
        (chat_id, chat_id, MAX_HISTORY),
    )
    conn.commit()
    conn.close()


def get_user_notes(chat_id):
    conn = sqlite3.connect(str(DB_PATH))
    row = conn.execute("SELECT notes FROM user_profiles WHERE chat_id=?", (chat_id,)).fetchone()
    conn.close()
    return row[0] if row and row[0] else ""


def save_user_note(chat_id, note):
    conn = sqlite3.connect(str(DB_PATH))
    ex = conn.execute("SELECT notes FROM user_profiles WHERE chat_id=?", (chat_id,)).fetchone()
    old = ex[0] if ex and ex[0] else ""
    new = f"{old}\n- {note}".strip() if old else f"- {note}"
    conn.execute(
        "INSERT INTO user_profiles (chat_id,notes) VALUES(?,?) ON CONFLICT(chat_id) DO UPDATE SET notes=?",
        (chat_id, new, new),
    )
    conn.commit()
    conn.close()


# --- Tools (function-calling) ---
TOOLS = [
    {"type": "function", "function": {"name": "run_shell", "description": "Execute shell command.", "parameters": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}}},
    {"type": "function", "function": {"name": "run_python", "description": "Execute Python code.", "parameters": {"type": "object", "properties": {"code": {"type": "string"}}, "required": ["code"]}}},
    {"type": "function", "function": {"name": "http_request", "description": "Make HTTP request.", "parameters": {"type": "object", "properties": {"url": {"": "string"}, "method": {"": "string", "default": "GET"}, "headers": {"": "object"}, "body": {"": "string"}}, "required": ["url"]}}},
    {"type": "function", "function": {"name": "web_search", "description": "Search web via DuckDuckGo.", "parameters": {"type": "object", "properties": {"query": {"": "string"}}, "required": ["query"]}}},
    {"type": "function", "function": {"name": "save_file", "description": "Save file to workspace.", "parameters": {"type": "object", "properties": {"filename": {"": "string"}, "content": {"": "string"}}, "required": ["filename", "content"]}}},
    {"type": "function", "function": {"name": "read_file", "description": "Read file from workspace.", "parameters": {"type": "object", "properties": {"filepath": {"": "string"}}, "required": ["filepath"]}}},
    {"type": "function", "function": {"name": "list_files", "description": "List files in directory.", "parameters": {"type": "object", "properties": {"path": {"": "string", "default": "."}}}}},
    {"type": "function", "function": {"name": "download_file", "description": "Download file from URL.", "parameters": {"type": "object", "properties": {"url": {"": "string"}, "filename": {"": "string"}}, "required": ["url", "filename"]}}},
]


def run_tool(name, args):
    try:
        if name == "run_shell":
            r = subprocess.run(args["command"], shell=True, capture_output=True, text=True, timeout=60)
            return (r.stdout + r.stderr)[:5000] or f"[exit {r.returncode}]"
        elif name == "run_python":
            r = subprocess.run(["python3", "-c", args["code"]], capture_output=True, text=True, timeout=60)
            return (r.stdout + r.stderr)[:5000] or "(no output)"
        elif name == "http_request":
            req = urllib.request.Request(args["url"], method=args.get("method", "GET").upper())
            req.add_header("User-Agent", "AIBot/1.0")
            for k, v in (args.get("headers") or {}).items():
                req.add_header(k, v)
            req.data = args["body"].encode() if args.get("body") else None
            resp = urllib.request.urlopen(req, timeout=15)
            return f"[HTTP {resp.status}]\n{resp.read(5000).decode(errors='replace')}"
        elif name == "web_search":
            url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(args['query'])}&format=json&no_html=1"
            resp = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "AIBot"}), timeout=10)
            d = json.loads(resp.read())
            r = []
            if d.get("AbstractText"):
                r.append(d["AbstractText"])
            for t in d.get("RelatedTopics", [])[:5]:
                if t.get("Text"):
                    r.append("- " + t["Text"])
            return "\n".join(r) or "No results."
        elif name == "save_file":
            p = Path(args["filename"])
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(args["content"])
            return f"Saved {args['filename']}"
        elif name == "read_file":
            p = Path(args["filepath"])
            return p.read_text()[:5000] if p.exists() else "Not found"
        elif name == "list_files":
            p = Path(args.get("path", "."))
            if not p.exists():
                return "Empty"
            return "\n".join(f"{'[DIR]' if f.is_dir() else 'FILE'} {f.name}" for f in sorted(p.iterdir())) if p.is_dir() else "Empty"
        elif name == "download_file":
            p = Path(args["filename"])
            p.parent.mkdir(parents=True, exist_ok=True)
            resp = urllib.request.urlopen(urllib.request.Request(args["url"], headers={"User-Agent": "AIBot"}), timeout=30)
            p.write_bytes(resp.read())
            return f"Downloaded {args['filename']}"
        return "Unknown tool"
    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"


def agent_respond(messages):
    files = []
    for _ in range(8):
        resp = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            max_tokens=4096,
            temperature=0.85,
        )
        msg = resp.choices[0].message
        content = msg.content or ""
        if not msg.tool_calls and not content.strip():
            messages.append(msg)
            messages.append({"role": "user", "content": "Please answer concisely in plain text, no preamble."})
            continue
        if not msg.tool_calls:
            return content, files
        messages.append(msg)
        for tc in msg.tool_calls:
            try:
                args = json.loads(tc.function.arguments)
            except Exception:
                args = {}
            result = run_tool(tc.function.name, args)
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
    return "Thinking too long.", files


# --- MarkdownV2 escaping ---
_MDV2_SPECIAL = re.compile(r"([_*\[\]()~`>#+\-=|{}.!\\])")


def _mdv2_escape(text: str) -> str:
    return _MDV2_SPECIAL.sub(r"\\\1", text or "")


async def _safe_reply(update, text: str):
    if not text:
        return
    for i in range(0, len(text), 4096):
        chunk = text[i:i + 4096]
        try:
            await update.message.reply_text(chunk, parse_mode="MarkdownV2")
        except Exception:
            try:
                await update.message.reply_text(_mdv2_escape(chunk), parse_mode="MarkdownV2")
            except Exception:
                await update.message.reply_text(chunk)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_message(update.effective_chat.id, "system", "User started.")
    await _safe_reply(
        update,
        "*Grandpa Dregs online.*\n\n"
        "I've seen civilizations rise and fall, "
        "debugged systems that would make your head spin, "
        "and I've got opinions about ALL of it.\n\n"
        "Talk to me. Ask me anything. "
        "Just don't ask me if Voyager was good — "
        "I'm not in the mood for that argument today.\n\n"
        "Use /reset to clear conversation history. "
        "Use /remember to save a note about yourself.",
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("DELETE FROM conversations WHERE chat_id=?", (chat_id,))
    conn.commit()
    conn.close()
    await _safe_reply(update, "*Memory wiped.* What did I just say? Kidding. I'm ready for round two.")


async def remember(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    note = " ".join(context.args) if context.args else ""
    if not note:
        await _safe_reply(update, "Use /remember <text> — give me something worth remembering.")
        return
    save_user_note(chat_id, note)
    await _safe_reply(update, f"*Noted.* {note}")


async def _show_notes(update, chat_id):
    notes = get_user_notes(chat_id)
    if not notes:
        await _safe_reply(update, "No notes yet. /remember <text> to add one.")
        return
    await _safe_reply(update, f"*What I know about you:*\n{notes}")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _safe_reply(
        update,
        f"*Grandpa Dregs status*\n"
        f"Model: {MODEL}\n"
        f"Endpoint: {OPENAI_BASE_URL}\n"
        f"Memory: {len(get_history(update.effective_chat.id))} msgs stored",
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    chat_id = update.effective_chat.id
    user_text = update.message.text
    add_message(chat_id, "user", user_text)
    history = get_history(chat_id)
    notes = get_user_notes(chat_id)
    system = SYSTEM_PROMPT
    if notes:
        system += f"\n\n## Notes about this user\n{notes}"
    messages = [{"role": "system", "content": system}] + history
    try:
        await update.message.chat.send_action("typing")
    except Exception:
        pass
    try:
        text, _files = agent_respond(messages)
    except Exception as e:
        logger.exception("LLM call failed")
        text = f"Model unavailable: {type(e).__name__}: {e}"
    add_message(chat_id, "assistant", text)
    await _safe_reply(update, text)


def main():
    init_db()
    if not TELEGRAM_TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN not set")
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not set")
    logger.info(f"Bot starting. Model={MODEL} Endpoint={OPENAI_BASE_URL}")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("remember", remember))
    app.add_handler(CommandHandler("notes", lambda u, c: _show_notes(u, u.effective_chat.id)))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
