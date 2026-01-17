import os
from pyrogram import Client, filters
from pyrogram.types import Message

# Configuration
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))
WEB_URL = os.environ.get("WEB_URL").rstrip('/')

bot = Client("bot_worker_session", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    await message.reply_text("Bot is active. Use /upload to host an HTML file.")

@bot.on_message(filters.command("upload") & filters.private)
async def upload_cmd(client, message):
    await message.reply_text("Please send me the **.html** file you wish to host.")

@bot.on_message(filters.document & filters.private)
async def handle_document(client, message: Message):
    if not message.document.file_name.endswith(".html"):
        await message.reply_text("❌ Error: Only .html files are supported.")
        return

    status = await message.reply_text("Processing file...")

    try:
        # Forward the file to the private channel to get a permanent message_id
        forwarded = await message.forward(CHANNEL_ID)
        
        # Generate the public link using the Web Service URL
        public_link = f"{WEB_URL}/html/{forwarded.id}"
        
        await status.edit(
            f"✅ **File Hosted Successfully!**\n\n"
            f"**Link:** {public_link}\n\n"
            f"Note: This link renders directly in the browser."
        )
    except Exception as e:
        await status.edit(f"❌ An error occurred: {str(e)}")

if __name__ == "__main__":
    print("Bot Worker is starting...")
    bot.run()
