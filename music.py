import os
import asyncio
import threading

# هذا السطر لازم يكون اول شي قبل اي استيراد ثاني
asyncio.set_event_loop(asyncio.new_event_loop())

from flask import Flask
from pyrogram import Client, filters
import yt_dlp

# سيرفر وهمي حتى Render ما يطفي البوت
app_web = Flask(__name__)
@app_web.route('/')
def home(): return "Bot Running 24/7"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

API_ID = 36047053
API_HASH = "e71f26b7e2bd148c6a30f401d837b7ad"
BOT_TOKEN = os.environ.get("BOT_TOKEN")

bot = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command(["play","شغل","p"]) & filters.group)
async def play(_, m):
    if len(m.command) < 2:
        return await m.reply("🎵 اكتب اسم الاغنية\nمثال: `شغل راشد الماجد`")
    song = " ".join(m.command[1:])
    msg = await m.reply(f"🔎 جاري البحث: {song}")
    try:
        opts = {'format': 'bestaudio[ext=m4a]', 'outtmpl': '%(title)s.%(ext)s', 'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{song}", download=True)
            data = info['entries'][0]
            file_name = ydl.prepare_filename(data)
        await _.send_audio(m.chat.id, file_name, title=data.get('title'), performer=data.get('uploader'), caption=f"✅ {data.get('title')}")
        os.remove(file_name)
        await msg.delete()
    except Exception as e:
        await msg.edit(f"❌ خطأ: {e}")

@bot.on_message(filters.command("start"))
async def start(_, m):
    await m.reply("🎧 بوت الاغاني شغال 24/7 ✅\nارسل في الكروب: شغل + اسم الاغنية")

bot.run()
