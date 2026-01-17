import os, asyncio
from flask import Flask, Response, abort
from pyrogram import Client
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

app = Flask(__name__)

client = Client(
    "html-fetch",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.route("/html/<int:msg_id>")
def serve(msg_id):

    async def fetch():
        async with client:
            msg = await client.get_messages(CHANNEL_ID, msg_id)
            if not msg or not msg.document:
                return None
            path = await msg.download()
            return open(path, "r", encoding="utf-8").read()

    html = asyncio.run(fetch())
    if not html:
        abort(404)

    return Response(html, mimetype="text/html")

@app.route("/")
def home():
    return "HTML Host Server Running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
