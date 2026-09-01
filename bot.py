import os, threading, json, re, asyncio
from flask import Flask
from telegram import Update, ChatPermissions
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
DB_FILE = "groups.json"

# سيرفر لـ Render المجاني - يحل مشكلة 409
flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "Kenan Bot - Management Bot Live"
def run_flask():
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
threading.Thread(target=run_flask, daemon=True).start()

def load_db():
    if not os.path.exists(DB_FILE): return {}
    try: return json.load(open(DB_FILE, 'r', encoding='utf-8'))
    except: return {}
def save_db(data):
    json.dump(data, open(DB_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
def get_group(chat_id):
    db = load_db()
    gid = str(chat_id)
    if gid not in db:
        db[gid] = {"active": False, "welcome": "هلا والله نورت الجروب ❤️", "locks": {"link": False, "spam": True, "photo": False}, "muted": []}
        save_db(db)
    return db[gid]

async def is_admin_async(update: Update):
    try:
        member = await update.effective_chat.get_member(update.effective_user.id)
        return member.status in ['administrator', 'creator']
    except: return False

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("هلا بيك 👋\nضيفني لجروب وارفعني ادمن ودز `تفعيل`")

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    gid = str(update.effective_chat.id)
    if gid in db and db[gid]["active"]:
        for member in update.message.new_chat_members:
            if member.is_bot: continue
            await update.message.reply_text(f"هلا {member.first_name} نورت الجروب {update.effective_chat.title} ❤️")

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    text = update.message.text.strip()
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    if update.effective_chat.type == 'private': return

    db = load_db()
    gid = str(chat_id)
    group = get_group(chat_id)
    admin = await is_admin_async(update)

    if user_id in group.get("muted", []) and not admin:
        try: await update.message.delete()
        except: pass
        return

    if group["active"]:
        if group["locks"].get("link") and re.search(r"(t\.me|https?://|www\.)", text.lower()):
            if not admin:
                try:
                    await update.message.delete()
                    await update.message.reply_text(f"ممنوع الروابط @{update.effective_user.username or update.effective_user.first_name} 🚫")
                except: pass
                return

    if text == "تفعيل":
        if not admin:
            await update.message.reply_text("هذا الامر للمشرفين فقط ⚠️")
            return
        db[gid]["active"] = True
        save_db(db)
        await update.message.reply_text(f"• المجموعه : {update.effective_chat.title}\n• تم تفعيلها ✅\n\nبواسطة : {update.effective_user.first_name}\nدز `اوامري` لمعرفة الاوامر")
        return

    if text == "تعطيل":
        if not admin: return
        db[gid]["active"] = False
        save_db(db)
        await update.message.reply_text("تم تعطيل الجروب ❌")
        return

    if not group["active"]: return

    if text in ["اوامري", "الاوامر", "اوامر"]:
        await update.message.reply_text(
            "**اوامر بوت Kenan 👑**\n\n"
            "🔹 تفعيل / تعطيل\n"
            "🔹 رفع ادمن / تنزيل ادمن - رد على الشخص\n"
            "🔹 كتم / الغاء كتم - رد على الشخص\n"
            "🔹 طرد / حظر - رد على الشخص\n"
            "🔹 قفل الروابط / فتح الروابط\n"
            "🔹 قفل الصور / فتح الصور\n"
            "🔹 اعدادات الحماية\n"
            "🔹 ايدي / الرابط\n"
            "🔹 همس + الرسالة\n\n"
            "ارفع البوت ادمن حتى تشتغل كل المميزات ✅",
            parse_mode='Markdown'
        )
        return

    if text in ["اعدادات الحماية", "الحماية"]:
        locks = group["locks"]
        await update.message.reply_text(f"⚙️ الحماية:\nالروابط: {'🔒' if locks['link'] else '🔓'}\nالسبام: {'🔒' if locks['spam'] else '🔓'}\nالصور: {'🔒' if locks['photo'] else '🔓'}")
        return

    if text == "قفل الروابط":
        if not admin: return
        db[gid]["locks"]["link"] = True
        save_db(db)
        await update.message.reply_text("تم قفل الروابط 🔒")
        return
    if text == "فتح الروابط":
        if not admin: return
        db[gid]["locks"]["link"] = False
        save_db(db)
        await update.message.reply_text("تم فتح الروابط 🔓")
        return

    if text.startswith("كتم") and update.message.reply_to_message:
        if not admin: return
        target = update.message.reply_to_message.from_user.id
        if target not in db[gid]["muted"]: db[gid]["muted"].append(target)
        save_db(db)
        try:
            await update.effective_chat.restrict_member(target, ChatPermissions(can_send_messages=False))
            await update.message.reply_text(f"تم كتم {update.message.reply_to_message.from_user.first_name} 🔇")
        except: await update.message.reply_text("ارفعني ادمن بكل الصلاحيات")
        return

    if text.startswith("الغاء كتم") and update.message.reply_to_message:
        if not admin: return
        target = update.message.reply_to_message.from_user.id
        if target in db[gid]["muted"]: db[gid]["muted"].remove(target)
        save_db(db)
        try:
            await update.effective_chat.restrict_member(target, ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True))
            await update.message.reply_text(f"تم الغاء كتم {update.message.reply_to_message.from_user.first_name} 🔊")
        except: pass
        return

    if text == "طرد" and update.message.reply_to_message:
        if not admin: return
        try:
            await update.effective_chat.ban_member(update.message.reply_to_message.from_user.id)
            await update.effective_chat.unban_member(update.message.reply_to_message.from_user.id)
            await update.message.reply_text("تم طرده 👋")
        except: await update.message.reply_text("ما اقدر اطرده")
        return

    if text in ["ايدي", "ايديي"]:
        await update.message.reply_text(f"ايديك: `{user_id}`\nايدي الجروب: `{chat_id}`", parse_mode='Markdown')
        return

    if text.startswith("همس "):
        try: await update.message.delete()
        except: pass
        await context.bot.send_message(chat_id, f"🔒 همسة: {text[4:]}\nمن: {update.effective_user.first_name}")
        return

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    # هذا السطر المهم يحل مشكلة الـ Conflict 409
    await app.bot.delete_webhook(drop_pending_updates=True)

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

    print("Kenan Management Bot Started - Fixed")
    await app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    asyncio.run(main())
