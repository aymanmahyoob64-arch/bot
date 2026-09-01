import os
import asyncio
from flask import Flask
from threading import Thread
from pyrogram import Client, filters
import yt_dlp

# حل مشكلة الـ Event Loop
try:
    asyncio.set_event_loop(asyncio.new_event_loop())
except:
    pass

# ويب سيرفر للـ Render
web = Flask(__name__)
@web.route('/')
def home(): return "Music Bot Running 24/7"
def run_web():
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port)

Thread(target=run_web, daemon=True).start()

API_ID = 36047053
API_HASH = "e71f26b7e2bd148c6a30f401d837b7ad"
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client("music24", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command(["play","شغل"]) & filters.group)
async def play(c, m):
    if len(m.command) < 2:
        return await m.reply("🎵 اكتب اسم الاغنية")
    song = " ".join(m.command[1:])
    status = await m.reply(f"🎧 جاري البحث عن: {song}")
    ydl_opts = {'format': 'bestaudio[ext=m4a]', 'outtmpl': '%(title)s.%(ext)s', 'quiet': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{song}", download=True)
            entry = info['entries'][0]
            file_path = ydl.prepare_filename(entry)
        await c.send_audio(m.chat.id, file_path, title=entry['title'], caption=f"✅ {entry['title']}")
        os.remove(file_path)
        await status.delete()
    except Exception as e:
        await status.edit(f"❌ {e}")

@app.on_message(filters.command("start"))
async def start(c,m):
    await m.reply("بوت اغاني 24/7 شغال ✅")

app.run()
