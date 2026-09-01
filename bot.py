import os, threading, json, re
from flask import Flask
from telegram import Update, ChatPermissions
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ChatMemberHandler

TOKEN = os.getenv("BOT_TOKEN")
DB_FILE = "groups.json"

# سيرفر لـ Render المجاني
flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "Kenan Bot - Management Bot Live"
def run_flask():
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
threading.Thread(target=run_flask, daemon=True).start()

# قاعدة بيانات بسيطة
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
        db[gid] = {"active": False, "welcome": "هلا والله نورت الجروب ❤️", "locks": {"link": False, "spam": True, "photo": False}, "admins": [], "muted": []}
        save_db(db)
    return db[gid]
def is_admin(update: Update):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    db = load_db()
    gid = str(chat_id)
    if gid in db and user_id in db[gid].get("admins", []): return True
    member = update.effective_chat.get_member(user_id)
    # This is sync in v20? we need async version below
    return False

async def is_admin_async(update: Update):
    try:
        member = await update.effective_chat.get_member(update.effective_user.id)
        return member.status in ['administrator', 'creator']
    except: return False

# --- الأوامر ---

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("هلا بيك 👋\nضيفني لجروب وارفعني ادمن ودز `تفعيل`")

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    text = update.message.text.strip()
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type

    if chat_type == 'private': return

    db = load_db()
    gid = str(chat_id)
    group = get_group(chat_id)
    admin = await is_admin_async(update)

    # تحقق من الحظر
    if user_id in group.get("muted", []):
        try: await update.message.delete()
        except: pass
        return

    # --- الحماية ---
    if group["active"]:
        # منع الروابط
        if group["locks"].get("link") and re.search(r"(t\.me|telegram\.me|https?://|www\.)", text.lower()):
            if not admin:
                try:
                    await update.message.delete()
                    await update.message.reply_text(f"@{update.effective_user.username or update.effective_user.first_name} ممنوع الروابط 🚫")
                except: pass
                return
        # منع التكرار والسبام (اذا رسالة طويلة جدا)
        if group["locks"].get("spam") and len(text) > 400:
            if not admin:
                try: await update.message.delete()
                except: pass
                return

    # --- اوامر التفعيل ---
    if text == "تفعيل":
        if not admin:
            await update.message.reply_text("هذا الامر للمشرفين فقط ⚠️")
            return
        db = load_db()
        db[gid]["active"] = True
        save_db(db)
        await update.message.reply_text(
            f"• المجموعه : {update.effective_chat.title}\n• تم تفعيلها مسبقا ✅\n\n"
            f"بواسطة : {update.effective_user.first_name}\n"
            f"دز `اوامري` لمعرفة الاوامر",
            reply_to_message_id=update.message.message_id
        )
        return

    if text == "تعطيل":
        if not admin: return
        db[gid]["active"] = False
        save_db(db)
        await update.message.reply_text("تم تعطيل الجروب ❌")
        return

    if not group["active"]: return

    # --- الاوامر ---
    if text in ["اوامري", "الاوامر", "اوامر"]:
        msg = """
**اوامر بوت Kenan 👑**

🔹 **اوامر الادارة:**
تفعيل / تعطيل
رفع ادمن / تنزيل ادمن
كتم / الغاء كتم
طرد / حظر / الغاء حظر
تثبيت / الغاء تثبيت

🔹 **اوامر الحماية:**
قفل الروابط / فتح الروابط
قفل الصور / فتح الصور
قفل السبام / فتح السبام
اعدادات الحماية

🔹 **اوامر عامة:**
الترحيب / ضع ترحيب
ايدي / ايديي
الرابط / معلومات الجروب

🔹 **الهمسات:**
همس + الرسالة
مثال: همس احبك

ارفع البوت ادمن حتى تشتغل كل المميزات ✅
"""
        await update.message.reply_text(msg)
        return

    if text in ["اعدادات الحماية", "الحماية"]:
        locks = group["locks"]
        await update.message.reply_text(
            f"⚙️ اعدادات الحماية:\n"
            f"الروابط: {'🔒 مقفول' if locks['link'] else '🔓 مفتوح'}\n"
            f"السبام: {'🔒 مقفول' if locks['spam'] else '🔓 مفتوح'}\n"
            f"الصور: {'🔒 مقفول' if locks['photo'] else '🔓 مفتوح'}"
        )
        return

    # قفل وفتح
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

    if text == "قفل الصور":
        if not admin: return
        db[gid]["locks"]["photo"] = True
        save_db(db)
        await update.message.reply_text("تم قفل الصور 🔒")
        return
    if text == "فتح الصور":
        if not admin: return
        db[gid]["locks"]["photo"] = False
        save_db(db)
        await update.message.reply_text("تم فتح الصور 🔓")
        return

    # كتم وطرد
    if text.startswith("كتم") and update.message.reply_to_message:
        if not admin: return
        target = update.message.reply_to_message.from_user.id
        if str(target) not in db[gid]["muted"]:
            db[gid]["muted"].append(target)
            save_db(db)
        try:
            await update.effective_chat.restrict_member(target, ChatPermissions(can_send_messages=False))
            await update.message.reply_text(f"تم كتم {update.message.reply_to_message.from_user.first_name} 🔇")
        except: await update.message.reply_text("ما اقدر اكتمه، ارفعني ادمن بكل الصلاحيات")
        return

    if text.startswith("الغاء كتم") and update.message.reply_to_message:
        if not admin: return
        target = update.message.reply_to_message.from_user.id
        if target in db[gid]["muted"]:
            db[gid]["muted"].remove(target)
            save_db(db)
        try:
            await update.effective_chat.restrict_member(target, ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True))
            await update.message.reply_text(f"تم الغاء كتم {update.message.reply_to_message.from_user.first_name} 🔊")
        except: pass
        return

    if text == "طرد" and update.message.reply_to_message:
        if not admin: return
        try:
            await update.effective_chat.ban_member(update.message.reply_to_message.from_user.id)
            await update.effective_chat.unban_member(update.message.reply_to_message.from_user.id)
            await update.message.reply_text("تم طرده من الجروب 👋")
        except: await update.message.reply_text("ما اقدر اطرده، ارفعني ادمن")
        return

    if text == "حظر" and update.message.reply_to_message:
        if not admin: return
        try:
            await update.effective_chat.ban_member(update.message.reply_to_message.from_user.id)
            await update.message.reply_text("تم حظره 🚫")
        except: await update.message.reply_text("ما اقدر احظره")
        return

    if text in ["ايدي", "ايديي"]:
        await update.message.reply_text(f"ايديك: `{user_id}`\nايدي الجروب: `{chat_id}`\nاسمك: {update.effective_user.first_name}", parse_mode='Markdown')
        return

    if text.startswith("همس "):
        secret = text[4:]
        await update.message.delete()
        await context.bot.send_message(chat_id, f"🔒 همسة سرية:\n{secret}\n\n(من {update.effective_user.first_name} - تظهر 5 ثواني وتنحذف)", disable_notification=True)
        return

# ترحيب بالأعضاء الجدد
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    gid = str(update.effective_chat.id)
    if gid in db and db[gid]["active"]:
        for member in update.message.new_chat_members:
            await update.message.reply_text(f"هلا {member.first_name} نورت الجروب {update.effective_chat.title} ❤️\n{db[gid]['welcome']}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
    print("Kenan Management Bot Started")
    app.run_polling()
