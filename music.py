import os
from pyrogram import Client, filters
import yt_dlp

API_ID = 36047053
API_HASH = "e71f26b7e2bd148c6a30f401d837b7ad"
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client("music24", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command(["play","شغل"]) & filters.group)
async def play(c, m):
    if len(m.command) < 2:
        return await m.reply("🎵 اكتب اسم الاغنية\nمثال: /play دجلة وفرات")

    song = " ".join(m.command[1:])
    status = await m.reply(f"🎧 **جاري تشغيل اغنية...**\n`{song}`")

    ydl_opts = {'format': 'bestaudio[ext=m4a]', 'outtmpl': '%(title)s.%(ext)s', 'quiet': True, 'no_warnings': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{song}", download=True)
            entry = info['entries'][0]
            file_path = ydl.prepare_filename(entry)

        await c.send_audio(m.chat.id, file_path, title=entry['title'], caption=f"✅ {entry['title']}")
        os.remove(file_path)
        await status.delete()
    except Exception as e:
        await status.edit(f"❌ خطا: {e}")

@app.on_message(filters.command("start"))
async def start(c,m):
    await m.reply("بوت اغاني 24/7 شغال ✅\nبالكروب اكتب /play اسم الاغنية")

app.run()
