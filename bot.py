import os, json, re, random
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("حط BOT_TOKEN في Render Environment Variables")

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE): return {}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return {}
def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
data = load_data()

def get_chat(chat_id):
    chat_id = str(chat_id)
    if chat_id not in data:
        data[chat_id] = {
            "activated": False,
            "locks": {"link": False, "english": False, "photo": False, "sticker": False, "gif": False, "bots": True, "porn": True},
            "admins": [], "mods": [], "special": [], "msgs": {}, "replies": {}
        }
    return data[chat_id]

app = Flask(__name__)
@app.route('/')
def home(): return "Bot Kenan Running"
Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000))), daemon=True).start()

OWNER_ID = 8149673627

def is_admin(update: Update):
    try:
        uid = update.effective_user.id
        if uid == OWNER_ID: return True
        chat = get_chat(update.effective_chat.id)
        if uid in chat["admins"]: return True
        member = update.effective_chat.get_member(uid)
        return member.status in ['administrator','creator']
    except: return False

def is_mod(update: Update):
    chat = get_chat(update.effective_chat.id)
    return is_admin(update) or update.effective_user.id in chat["mods"]

def activate(update: Update, context: CallbackContext):
    chat = get_chat(update.effective_chat.id)
    chat["activated"] = True
    save_data()
    update.message.reply_text(f"✅ تم تفعيل المجموعة {update.effective_chat.title}")

def deactivate(update: Update, context: CallbackContext):
    if not is_admin(update): return
    get_chat(update.effective_chat.id)["activated"] = False
    save_data()
    update.message.reply_text("❌ تم تعطيل المجموعه")

def my_id(update: Update, context: CallbackContext):
    chat = get_chat(update.effective_chat.id)
    if not chat["activated"]: return
    user = update.effective_user
    target = user
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user

    count = chat["msgs"].get(str(target.id), 0)

    if target.id == OWNER_ID:
        rank = "المالك الاساسي"
        title = "المالك"
    elif target.id in chat["admins"]:
        rank = "مشرف"
        title = "مشرف"
    elif target.id in chat["mods"]:
        rank = "ادمن"
        title = "ادمن"
    else:
        rank = "عضو"
        title = "عضو"

    username = f"@{target.username}" if target.username else "لا يوجد"

    caption = f"جبر لقلبي قبل قلوبهم 💛.\n\n- NAME : {target.first_name} 𓅓.\n- UsEr : {username} 𓅓.\n- MsG : {count} متوسط 𓅓.\n- StA : {rank} 𓅓.\n- ID : {target.id} 𓅓.\n- TITLE {title} 𓅓.\n- BIO I don't need to impress you. 𓆩 𓅓."

    try:
        photos = context.bot.get_user_profile_photos(target.id, limit=1)
        if photos.total_count > 0:
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=photos.photos[0][-1].file_id, caption=caption)
        else:
            update.message.reply_text(caption)
    except:
        update.message.reply_text(caption)

def handle_all(update: Update, context: CallbackContext):
    if update.effective_chat.type == 'private': return
    chat = get_chat(update.effective_chat.id)
    if not chat["activated"]: return
    uid = str(update.effective_user.id)
    chat["msgs"][uid] = chat["msgs"].get(uid, 0) + 1
    text = update.message.text or ""
    if not is_mod(update):
        if chat["locks"]["link"] and ("t.me" in text or "http" in text or "telegram.me" in text):
            try: update.message.delete(); return
            except: pass
        if chat["locks"]["english"] and re.search(r'[a-zA-Z]', text):
            try: update.message.delete(); return
            except: pass
        bad = ["كس","طيز","زب","نيك","porn","xxx"]
        if chat["locks"]["porn"] and any(w in text.lower() for w in bad):
            try: update.message.delete()
            except: pass
            return
    if text in chat["replies"]:
        update.message.reply_text(chat["replies"][text])
    save_data()

def promote_admin(update: Update, context: CallbackContext):
    if not is_admin(update): return
    if not update.message.reply_to_message: return update.message.reply_text("رد على الشخص لرفعه")
    target = update.message.reply_to_message.from_user
    chat = get_chat(update.effective_chat.id)
    if target.id not in chat["admins"]: chat["admins"].append(target.id)
    save_data()
    update.message.reply_text(f"✅ تم رفع {target.first_name} مشرف")

def promote_mod(update: Update, context: CallbackContext):
    if not is_admin(update): return
    if not update.message.reply_to_message: return
    target = update.message.reply_to_message.from_user
    chat = get_chat(update.effective_chat.id)
    if target.id not in chat["mods"]: chat["mods"].append(target.id)
    save_data()
    update.message.reply_text(f"✅ تم رفع {target.first_name} ادمن")

def ban_user(update: Update, context: CallbackContext):
    if not is_mod(update): return
    if update.message.reply_to_message:
        try:
            context.bot.kick_chat_member(update.effective_chat.id, update.message.reply_to_message.from_user.id)
            update.message.reply_text("🚫 تم طرده")
        except: update.message.reply_text("ما اكدر اطرده - ارفعني مشرف")

def lock_cmd(update: Update, context: CallbackContext):
    if not is_admin(update): return
    text = update.message.text.replace("قفل ","").strip()
    chat = get_chat(update.effective_chat.id)
    mapping = {"الروابط":"link","الانجليزيه":"english","الانجليزية":"english","الاباحي":"porn","الكل":"all"}
    if text in mapping:
        if text=="الكل":
            for k in chat["locks"]: chat["locks"][k]=True
        else:
            chat["locks"][mapping[text]]=True
        save_data()
        update.message.reply_text(f"🔒 تم قفل {text}")

def unlock_cmd(update: Update, context: CallbackContext):
    if not is_admin(update): return
    text = update.message.text.replace("فتح ","").strip()
    chat = get_chat(update.effective_chat.id)
    mapping = {"الروابط":"link","الانجليزيه":"english","الانجليزية":"english","الاباحي":"porn","الكل":"all"}
    if text in mapping:
        if text=="الكل":
            for k in chat["locks"]: chat["locks"][k]=False
        else:
            chat["locks"][mapping[text]]=False
        save_data()
        update.message.reply_text(f"🔓 تم فتح {text}")

def add_reply_cmd(update: Update, context: CallbackContext):
    if not is_admin(update): return
    txt = update.message.text.replace("اضف رد ","")
    if "|" not in txt: return update.message.reply_text("الصيغة: اضف رد هلا | اهلا حبي")
    k,v = txt.split("|",1)
    chat = get_chat(update.effective_chat.id)
    chat["replies"][k.strip()] = v.strip()
    save_data()
    update.message.reply_text(f"✅ تم حفظ رد {k.strip()}")

def fun(update: Update, context: CallbackContext):
    t = update.message.text
    if "زواج" in t: update.message.reply_text(f"💍 زواج {update.effective_user.first_name} من {random.choice(['سوما','كنان','توتا'])} 😂")
    elif "نسبه الحب" in t or "نسبة الحب" in t: update.message.reply_text(f"❤️ نسبة الحب {random.randint(1,100)}%")

def start(update: Update, context: CallbackContext):
    update.message.reply_text("✅ بوت كنان شغال\nاكتب تفعيل بالجروب")

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.regex("^تفعيل$"), activate))
dp.add_handler(MessageHandler(Filters.regex("^تعطيل$"), deactivate))
dp.add_handler(MessageHandler(Filters.regex("^(ايدي|id|ا)$"), my_id))
dp.add_handler(MessageHandler(Filters.regex("^رفع مشرف$"), promote_admin))
dp.add_handler(MessageHandler(Filters.regex("^رفع ادمن$"), promote_mod))
dp.add_handler(MessageHandler(Filters.regex("^(حظر|طرد)$"), ban_user))
dp.add_handler(MessageHandler(Filters.regex("^قفل"), lock_cmd))
dp.add_handler(MessageHandler(Filters.regex("^فتح"), unlock_cmd))
dp.add_handler(MessageHandler(Filters.regex("^اضف رد"), add_reply_cmd))
dp.add_handler(MessageHandler(Filters.regex("زواج|نسبه الحب|نسبة الحب"), fun))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_all))

print("Bot is running...")
updater.start_polling()
updater.idle()
