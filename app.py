import os
import asyncio
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

# -------------------------
# Serve HTML by message_id
# -------------------------
@app.route("/html/<int:msg_id>")
def serve_html(msg_id):

    async def fetch():
        async with bot:
            msg = await bot.get_messages(CHANNEL_ID, msg_id)
            if not msg or not msg.document:
                return None
            file_path = await msg.download()
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()

    html = asyncio.run(fetch())
    if not html:
        abort(404)

    return Response(html, mimetype="text/html")


@app.route("/")
def home():
    return "HTML Host Bot is running"


# -------------------------
# Telegram BOT PART
# -------------------------
@bot.on_message(filters.command("upload") & filters.private)
async def upload_html(client, message):
    await message.reply_text(
        "HTML file bhejo (.html)\n"
        "Main uska public link de dunga."
    )

@bot.on_message(filters.document & filters.private)
async def handle_html(client, message):

    if not message.document.file_name.endswith(".html"):
        await message.reply_text("Sirf .html file allowed hai")
        return

    # Forward HTML file to private channel
    sent = await message.forward(CHANNEL_ID)

    link = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/html/{sent.id}"

    await message.reply_text(
        f"✅ HTML Uploaded Successfully\n\n"
        f"🌐 Public Link:\n{link}"
    )


# -------------------------
# Run both Flask + Bot
# -------------------------
def run_bot():
    bot.run()

if __name__ == "__main__":
    import threading
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
