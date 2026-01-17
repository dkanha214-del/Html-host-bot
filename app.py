import os
from pyrogram import Client, filters
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
WEB_URL = os.getenv("WEB_URL")  # Flask service URL

bot = Client(
    "html-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@bot.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply_text("✅ Bot Ready\nUse /upload")

@bot.on_message(filters.command("upload") & filters.private)
async def upload(client, message):
    await message.reply_text("Send .html file")

@bot.on_message(filters.document & filters.private)
async def handle(client, message):

    if not message.document.file_name.endswith(".html"):
        await message.reply_text("❌ Only .html allowed")
        return

    sent = await message.forward(CHANNEL_ID)
    link = f"{WEB_URL}/html/{sent.id}"

    await message.reply_text(
        f"✅ Uploaded\n\n🌐 {link}"
    )

bot.run()
