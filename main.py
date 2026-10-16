import asyncio
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

import os
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
import yt_dlp

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

API_ID = 25463867
API_HASH = "f8616f4968fb92904faa7c4790e2eb27"
BOT_TOKEN = "8673101411:AAF5wYZ2ApMiXCoBVCmGNBJJuZ6_Cy4eiP4"

app = Client("SpaidyMusicBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

IS_ACTIVE = True

RUSSIAN_DESC = (
    "Музыкальный бот для поиска и прослушивания треков в Telegram. "
    "Быстрое воспроизведение музыки высокого качества в группах."
)

YTDL_OPTS = {
    "format": "bestaudio/best",
    "outtmpl": "downloads/%(id)s.%(ext)s",
    "quiet": True,
    "no_warnings": True,
    "nocheckcertificate": True,
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "192",
    }],
}

@app.on_message(filters.command("start") & filters.private)
async def start_private(client: Client, message: Message):
    bot_info = await client.get_me()
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("اضفني لمجموعتي", url=f"https://t.me/{bot_info.username}?startgroup=true")]
    ])
    text = f"𝐒𝐩𝐚𝐢𝐝𝐲 𝐦𝐮𝐬𝐢𝐜\n\n{RUSSIAN_DESC}"
    await message.reply_text(text, reply_markup=markup)

@app.on_message(filters.regex(r"^تفعيل سبايدي$"))
async def enable_bot(client: Client, message: Message):
    global IS_ACTIVE
    IS_ACTIVE = True
    await message.reply_text("تم تفعيل سبايدي بنجاح")

@app.on_message(filters.regex(r"^تعطيل سبايدي$"))
async def disable_bot(client: Client, message: Message):
    global IS_ACTIVE
    IS_ACTIVE = False
    await message.reply_text("تم تعطيل سبايدي بنجاح")

@app.on_message(filters.regex(r"^(سبايدي|يوت)\s+(.+)$"))
async def search_music(client: Client, message: Message):
    if not IS_ACTIVE:
        return

    match = re.match(r"^(سبايدي|يوت)\s+(.+)$", message.text.strip())
    if not match:
        return

    query = match.group(2).strip()
    status = await message.reply_text("سبايدي يبحث...")

    try:
        os.makedirs("downloads", exist_ok=True)
        # البحث في ساوندكلاود بدون المرور على يوتيوب المحظور
        with yt_dlp.YoutubeDL(YTDL_OPTS) as ytdl:
            info = ytdl.extract_info(f"scsearch1:{query}", download=True)["entries"][0]
            audio_id = info["id"]
            title = info.get("title", query)
            performer = info.get("uploader", "Spaidy Music")
            duration = int(info.get("duration", 0))
            audio_file = f"downloads/{audio_id}.mp3"

        await message.reply_audio(
            audio=audio_file,
            title=title,
            performer=performer,
            duration=duration
        )
        await status.delete()

        if os.path.exists(audio_file):
            os.remove(audio_file)

    except Exception as e:
        await status.edit_text(f"خطأ: {str(e)}")

if __name__ == "__main__":
    print("𝐒𝐩𝐚𝐢𝐝𝐲 𝐦𝐮𝐬𝐢𝐜 يعمل الآن بنجاح!")
    app.run()
