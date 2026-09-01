import os
import asyncio
asyncio.set_event_loop(asyncio.new_event_loop())

from pyrogram import Client, filters
import yt_dlp

API_ID = 36047053
API_HASH = "e71f26b7e2bd148c6a30f401d837b7ad"
BOT_TOKEN = os.environ.get("BOT_TOKEN")

bot = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command(["play","شغل","p"]) & filters.group)
async def play(_, m):
    if len(m.command) < 2:
        return await m.reply("🎵 اكتب اسم الاغنية")
    song = " ".join(m.command[1:])
    msg = await m.reply(f"🔎 جاري البحث: {song}")
    try:
        opts = {'format': 'bestaudio[ext=m4a]', 'outtmpl': '%(title)s.%(ext)s', 'quiet': True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{song}", download=True)
            data = info['entries'][0]
            file_name = ydl.prepare_filename(data)
        await _.send_audio(m.chat.id, file_name, title=data.get('title'), caption=f"✅ {data.get('title')}")
        os.remove(file_name)
        await msg.delete()
    except Exception as e:
        await msg.edit(f"❌ {e}")

@bot.on_message(filters.command("start"))
async def start(_, m):
    await m.reply("🎧 بوت الاغاني شغال 24/7 ✅")

bot.run()
