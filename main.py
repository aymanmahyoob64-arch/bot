import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ChatPrivileges
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioVideoPiped

# ==================== 1. الإعدادات وقراءة المتغيرات ====================
API_ID = int(os.environ.get("API_ID", "123456"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

app = Client("pro_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call_py = PyTgCalls(app)

# قاعدة بيانات مؤقتة للردود التلقائية
AUTO_RESPONSES = {
    "السلام عليكم": "وعليكم السلام ورحمة الله وبركاته! أنورت المجموعة 🌹",
    "البوت": "أنا في الخدمة! أرسل /help لمعرفة الأوامر 🤖",
    "تفعيل": "تم تفعيل الحماية والخدمات بنجاح ✅"
}

# ==================== 2. تشغيل الصوت والفيديو ====================
@app.on_message(filters.command(["تشغيل", "play"]) & filters.group)
async def play_audio_video(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❌ يرجى كتابة اسم الأغنية أو الرابط بعد الأمر.\nمثال: `تشغيل أغنية`")
    
    query = message.text.split(None, 1)[1]
    status_msg = await message.reply_text("🔍 جاري البحث والمزامنة مع المكالمة...")
    
    cmd = f'yt-dlp -g -f "best[height<=720]" "ytsearch:{query}"'
    proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, _ = await proc.communicate()
    
    urls = stdout.decode().strip().split('\n')
    if not urls or len(urls) < 1 or not urls[0]:
        return await status_msg.edit_text("❌ لم يتم العثور على نتائج.")
    
    stream_url = urls[0]
    
    try:
        await call_py.join_group_call(
            message.chat.id,
            AudioVideoPiped(stream_url)
        )
        await status_msg.edit_text(f"🎬 **تم التشغيل بنجاح!**\n🎵 **الطلب:** `{query}`")
    except Exception as e:
        await status_msg.edit_text(f"❌ تعذر الانضمام للمكالمة. تأكد من فتح المكالمة الجماعية وأذونات البوت.\n`التفاصيل: {e}`")

@app.on_message(filters.command(["ايقاف", "stop"]) & filters.group)
async def stop_stream(_, message: Message):
    try:
        await call_py.leave_group_call(message.chat.id)
        await message.reply_text("🔇 تم إيقاف التشغيل والمغادرة من المكالمة.")
    except Exception:
        await message.reply_text("❌ البوت غير متصل بمكالمة حالياً.")

# ==================== 3. رفع وإدارة الأعضاء ====================
@app.on_message(filters.command(["رفع مشرف", "ارفعني"]) & filters.group)
async def promote_member(client: Client, message: Message):
    user = await client.get_chat_member(message.chat.id, message.from_user.id)
    if user.status.value not in ["administrator", "owner"]:
        return await message.reply_text("❌ هذا الأمر مخصص للمشرفين فقط.")
    
    if not message.reply_to_message:
        return await message.reply_text("❌ قم بالرد على رسالة الشخص الذي تريد رفعه مديراً.")
    
    target_user = message.reply_to_message.from_user
    try:
        await client.promote_chat_member(
            message.chat.id,
            target_user.id,
            privileges=ChatPrivileges(
                can_manage_chat=True,
                can_delete_messages=True,
                can_manage_video_chats=True,
                can_restrict_members=True,
                can_promote_members=False
            )
        )
        await message.reply_text(f"✅ تم رفع العضو [{target_user.first_name}](tg://user?id={target_user.id}) مشرفاً بنجاح!")
    except Exception as e:
        await message.reply_text(f"❌ تعذر ترقية العضو. تأكد من إعطاء البوت صلاحية \"إضافة مشرفين جدد\".\n`{e}`")

# ==================== 4. نظام الحماية ====================
@app.on_message(filters.group & (filters.regex(r"t\.me/") | filters.regex(r"telegram\.me/")))
async def anti_link_protection(client: Client, message: Message):
    user = await client.get_chat_member(message.chat.id, message.from_user.id)
    if user.status.value in ["administrator", "owner"]:
        return
    
    try:
        await message.delete()
        warning = await message.reply_text(f"⚠️ يمنع إرسال الروابط داخل المجموعة يا [{message.from_user.first_name}](tg://user?id={message.from_user.id})!")
        await asyncio.sleep(5)
        await warning.delete()
    except Exception:
        pass

# ==================== 5. الردود التلقائية ====================
@app.on_message(filters.group & filters.text & ~filters.bot, group=1)
async def auto_reply(_, message: Message):
    text = message.text.strip()
    if text in AUTO_RESPONSES:
        await message.reply_text(
            AUTO_RESPONSES[text],
            reply_to_message_id=message.id
        )

# ==================== 6. قسم الترفيه ====================
@app.on_message(filters.command(["حظ", "كت تويت"]) & filters.group)
async def entertainment_commands(_, message: Message):
    cmd = message.command[0]
    import random
    if cmd == "حظ":
        fortunes = ["حظك اليوم ممتاز 🌟", "انتبه لقراراتك اليوم ⚠️", "خبر سعيد في الطريق إليك 🎁", "يوم هادئ ومريح ☕"]
        await message.reply_text(f"🎲 **حظك اليوم:** {random.choice(fortunes)}")
    elif cmd == "كت تويت":
        questions = [
            "ما هي العادة التي تتمنى التخلص منها؟",
            "شيء لو يعود بك الزمن لن تفعله؟",
            "أجمل مدينة زرتها في حياتك؟"
        ]
        await message.reply_text(f"💬 **كت تويت:**\n{random.choice(questions)}")

# ==================== 7. الترحيب ====================
@app.on_message(filters.command(["start", "help"]))
async def start_command(_, message: Message):
    me = await app.get_me()
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ إضافـة البوت للمجموعة", url=f"https://t.me/{me.username}?startgroup=true")]
    ])
    welcome_text = (
        f"أهلاً بك **{message.from_user.first_name}** في بوت الإدارة والتشغيل الشامل! 🚀\n\n"
        "💡 **الأوامر المتاحة:**\n"
        "• `تشغيل` + اسم الأغنية/الفيديو (في المجموعات)\n"
        "• `ايقاف` لإيقاف تشغيل الصوت/الفيديو\n"
        "• `رفع مشرف` بالرد على الشخص\n"
        "• `حظ` / `كت تويت` للترفيه"
    )
    await message.reply_text(welcome_text, reply_markup=buttons)

# ==================== التشغيل ====================
async def main():
    await app.start()
    await call_py.start()
    print("🤖 البوت يعمل بنجاح الآن!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
