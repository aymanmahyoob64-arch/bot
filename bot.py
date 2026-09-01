import os, threading, json, re
from flask import Flask
from telegram import Update, ChatPermissions, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

TOKEN = os.getenv("BOT_TOKEN")
DB_FILE = "groups.json"

flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "Kenan Bot Live"
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
        db[gid] = {"active": False, "welcome": "هلا والله نورت الجروب ❤️", "locks": {"link": False, "spam": True}, "muted": []}
        save_db(db)
    return db[gid]

async def is_admin_async(update: Update):
    try:
        member = await update.effective_chat.get_member(update.effective_user.id)
        return member.status in ['administrator', 'creator']
    except: return False

async def start_cmd(update, context):
    await update.message.reply_text("هلا بيك 👋 ضيفني لجروب وارفعني ادمن ودز تفعيل")

async def welcome(update, context):
    db = load_db()
    gid = str(update.effective_chat.id)
    if gid in db and db[gid]["active"]:
        for m in update.message.new_chat_members:
            if not m.is_bot:
                await update.message.reply_text(f"هلا {m.first_name} نورت الجروب ❤️")

async def handle_messages(update: Update, context):
    if not update.message or not update.message.text: return
    text = update.message.text.strip()
    chat_id = update.effective_chat.id
    if update.effective_chat.type == 'private': return

    db = load_db()
    gid = str(chat_id)
    group = get_group(chat_id)
    admin = await is_admin_async(update)

    if update.effective_user.id in group.get("muted", []) and not admin:
        try: await update.message.delete()
        except: pass
        return

    if group["active"] and group["locks"].get("link") and re.search(r"(t\.me|https?://|www\.)", text.lower()):
        if not admin:
            try:
                await update.message.delete()
                await update.message.reply_text(f"ممنوع الروابط @{update.effective_user.username or update.effective_user.first_name} 🚫")
            except: pass
            return

    if text == "تفعيل":
        if not admin:
            await update.message.reply_text("للمشرفين فقط ⚠️")
            return
        db[gid]["active"] = True
        save_db(db)
        await update.message.reply_text(f"تم تفعيل الجروب {update.effective_chat.title} ✅\nدز اوامري")
        return

    if text == "تعطيل":
        if not admin: return
        db[gid]["active"] = False
        save_db(db)
        await update.message.reply_text("تم التعطيل ❌")
        return

    if not group["active"]: return

    if text in ["اوامري","الاوامر","اوامر"]:
        await update.message.reply_text(
            "اوامر Kenan 👑\n\nتفعيل / تعطيل\nكتم / الغاء كتم (رد)\nطرد / حظر (رد)\nقفل الروابط / فتح الروابط\nاعدادات الحماية\nايدي\nهمس + رسالة"
        )
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
        except: await update.message.reply_text("ارفعني ادمن")
        return

    if text.startswith("الغاء كتم") and update.message.reply_to_message:
        if not admin: return
        target = update.message.reply_to_message.from_user.id
        if target in db[gid]["muted"]: db[gid]["muted"].remove(target)
        save_db(db)
        try:
            await update.effective_chat.restrict_member(target, ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True))
            await update.message.reply_text("تم الغاء الكتم 🔊")
        except: pass
        return

    if text == "طرد" and update.message.reply_to_message:
        if not admin: return
        try:
            await update.effective_chat.ban_member(update.message.reply_to_message.from_user.id)
            await update.effective_chat.unban_member(update.message.reply_to_message.from_user.id)
            await update.message.reply_text("تم الطرد 👋")
        except: await update.message.reply_text("ما اقدر")
        return

    if text in ["ايدي","ايديي"]:
        await update.message.reply_text(f"ايديك: {update.effective_user.id}")
        return

if __name__ == "__main__":
    import asyncio
    async def del_hook():
        try:
            b = Bot(token=TOKEN)
            await b.delete_webhook(drop_pending_updates=True)
            print("Webhook deleted")
        except Exception as e:
            print(e)
    asyncio.run(del_hook())

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
    print("Bot Started")
    app.run_polling(drop_pending_updates=True)
