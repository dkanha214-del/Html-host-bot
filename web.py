import os
import asyncio
from flask import Flask, Response, abort
from pyrogram import Client

# Configuration
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))
PORT = int(os.environ.get("PORT", 8080))

app = Flask(__name__)

# Initialize Pyrogram Client for the Web Service
# We use a separate session name to avoid SQLite locks
web_tg_app = Client("web_server_session", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def download_html_content(message_id):
    """Downloads the file into memory and returns the string content."""
    async with web_tg_app:
        try:
            message = await web_tg_app.get_messages(CHANNEL_ID, message_id)
            if not message or not message.document:
                return None
            
            # Download file as a byte stream in memory
            file_bytes = await web_tg_app.download_media(message, in_memory=True)
            return file_bytes.getbuffer().tobytes()
        except Exception as e:
            print(f"Error fetching message {message_id}: {e}")
            return None

@app.route('/html/<int:message_id>')
def serve_html(message_id):
    """Route to fetch and render HTML."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    content = loop.run_until_complete(download_html_content(message_id))
    loop.close()

    if content:
        return Response(content, mimetype='text/html')
    else:
        return abort(404, description="HTML file not found or expired.")

@app.route('/')
def index():
    return "HTML Hosting Service is Online."

if __name__ == "__main__":
    # Render requires binding to 0.0.0.0
    app.run(host='0.0.0.0', port=PORT)
