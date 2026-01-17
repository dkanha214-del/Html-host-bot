import os
import asyncio
import threading
from flask import Flask, Response, abort
from pyrogram import Client, filters
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

bot = Client(
    "html-host-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

app = Flask(__name__)

# --------------------
# Flask: Serve HTML
# --------------------
@app.route("/html/<int:msg_id>")
def serve_html(msg_id):

    async def fetch():
        msg = await bot.get_messages(CHANNEL_ID, msg_id)
        if not msg or not msg.document:
            return None
        path = await msg.download()
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    html = asyncio.run(fetch())
    if not html:
        abort(404)

    return Response(html, mimetype="text/html")


@app.route("/")
def home():
    return "HTML Host Bot is running"


# --------------------
# Telegram Handlers
# --------------------
@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    await message.reply_text(
        "✅ Bot Active\n\n"
        "Use /upload and send .html file"
    )

@bot.on_message(filters.command("upload") & filters.private)
async def upload_cmd(client, message):
    await message.reply_text("Send your .html file")

@bot.on_message(filters.document & filters.private)
async def handle_file(client, message):

    if not message.document.file_name.endswith(".html"):
        await message.reply_text("❌ Only .html files allowed")
        return

    sent = await message.forward(CHANNEL_ID)
    host = os.getenv("RENDER_EXTERNAL_HOSTNAME")

    link = f"https://{host}/html/{sent.id}"

    await message.reply_text(
        "✅ Uploaded Successfully\n\n"
        f"🌐 Public Link:\n{link}"
    )


# --------------------
# Start Bot (CORRECT)
# --------------------
async def start_bot():
    await bot.start()
    print("Bot started")
    await asyncio.Event().wait()  # keep alive

def run_bot():
    asyncio.run(start_bot())


if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
