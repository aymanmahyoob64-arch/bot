import os, json, re, random
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = os.environ.get("BOT_TOKEN")
DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE): return {}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f: return json.load(f)
    except: return {}
def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=2)
data = load_data()

def get_chat(cid):
    cid=str(cid)
    if cid not in data:
        data[cid]={"activated":False,"locks":{"link":False,"english":False,"porn":True,"photo":False,"sticker":False},"admins":[],"mods":[],"special":[],"msgs":{},"replies":{}}
    return data[cid]

app = Flask(__name__)
@app.route('/')
def home(): return "KENAN BOT LIVE"
Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000))), daemon=True).start()

OWNER=8149673627
def is_admin(u):
    try:
        if u.effective_user.id==OWNER: return True
        if u.effective_user.id in get_chat(u.effective_chat.id)["admins"]: return True
        return u.effective_chat.get_member(u.effective_user.id).status in ['administrator','creator']
    except: return False
def is_mod(u): return is_admin(u) or u.effective_user.id in get_chat(u.effective_chat.id)["mods"]

def activate(u,c):
    get_chat(u.effective_chat.id)["activated"]=True; save_data()
    u.message.reply_text(f"✅ تم تفعيل {u.effective_chat.title}")
def deactivate(u,c):
    if not is_admin(u): return
    get_chat(u.effective_chat.id)["activated"]=False; save_data()
    u.message.reply_text("❌ تم تعطيل المجموعة")

def id_cmd(u,c):
    ch=get_chat(u.effective_chat.id)
    if not ch["activated"]: return
    user=u.effective_user
    if u.message.reply_to_message: user=u.message.reply_to_message.from_user
    cnt=ch["msgs"].get(str(user.id),0)
    rank="المالك" if user.id==OWNER else "مشرف" if user.id in ch["admins"] else "ادمن" if user.id in ch["mods"] else "عضو"
    u.message.reply_text(f"👤 ايدي\n• الاسم: {user.first_name}\n• اليوزر: @{user.username or 'لا يوجد'}\n• الايدي: `{user.id}`\n• الرسائل: {cnt}\n• الرتبة: {rank}\n• الجروب: {u.effective_chat.title}", parse_mode='Markdown')

def handle(u,c):
    if u.effective_chat.type=='private': return
    ch=get_chat(u.effective_chat.id)
    if not ch["activated"]: return
    uid=str(u.effective_user.id)
    ch["msgs"][uid]=ch["msgs"].get(uid,0)+1
    txt=u.message.text or ""
    # ردود
    if txt in ch["replies"]: u.message.reply_text(ch["replies"][txt])
    # حماية
    if not is_mod(u):
        if ch["locks"]["link"] and ("t.me" in txt or "http" in txt):
            try: u.message.delete(); return
            except: pass
        if ch["locks"]["english"] and re.search(r'[a-zA-Z]', txt):
            try: u.message.delete(); return
            except: pass
        if ch["locks"]["porn"] and any(w in txt.lower() for w in ["كس","طيز","زب","نيك","porn"]):
            try: u.message.delete(); return
            except: pass
    save_data()

def lock(u,c):
    if not is_admin(u): return
    t=u.message.text.replace("قفل","").strip()
    ch=get_chat(u.effective_chat.id); m={"الروابط":"link","الانجليزيه":"english","الانجليزية":"english","الاباحي":"porn","الصور":"photo","الملصقات":"sticker","الكل":"all"}
    if t in m:
        if t=="الكل":
            for k in ch["locks"]: ch["locks"][k]=True
        else: ch["locks"][m[t]]=True
        save_data(); u.message.reply_text(f"🔒 تم قفل {t}")

def unlock(u,c):
    if not is_admin(u): return
    t=u.message.text.replace("فتح","").strip()
    ch=get_chat(u.effective_chat.id); m={"الروابط":"link","الانجليزيه":"english","الانجليزية":"english","الاباحي":"porn","الصور":"photo","الملصقات":"sticker","الكل":"all"}
    if t in m:
        if t=="الكل":
            for k in ch["locks"]: ch["locks"][k]=False
        else: ch["locks"][m[t]]=False
        save_data(); u.message.reply_text(f"🔓 تم فتح {t}")

def add_reply(u,c):
    if not is_admin(u): return
    txt=u.message.text.replace("اضف رد","").strip()
    if "|" not in txt: return u.message.reply_text("استخدم: اضف رد هلا | اهلين")
    k,v=txt.split("|",1); ch=get_chat(u.effective_chat.id); ch["replies"][k.strip()]=v.strip(); save_data()
    u.message.reply_text(f"✅ تم اضافة رد {k.strip()}")

def del_reply(u,c):
    if not is_admin(u): return
    k=u.message.text.replace("حذف رد","").replace("مسح رد","").strip()
    ch=get_chat(u.effective_chat.id)
    if k in ch["replies"]: del ch["replies"][k]; save_data(); u.message.reply_text("🗑 تم حذف الرد")
    else: u.message.reply_text("الرد غير موجود")

def ban(u,c):
    if not is_mod(u): return
    if u.message.reply_to_message:
        try: c.bot.kick_chat_member(u.effective_chat.id, u.message.reply_to_message.from_user.id); u.message.reply_text("🚫 تم الطرد")
        except: u.message.reply_text("ارفعني مشرف اول")

def promote(u,c,role):
    if not is_admin(u): return
    if not u.message.reply_to_message: return u.message.reply_text("رد على الشخص")
    tgt=u.message.reply_to_message.from_user; ch=get_chat(u.effective_chat.id)
    lst=ch["admins"] if role=="مشرف" else ch["mods"] if role=="ادمن" else ch["special"]
    if tgt.id not in lst: lst.append(tgt.id)
    save_data(); u.message.reply_text(f"✅ تم رفع {tgt.first_name} {role}")

def fun(u,c):
    txt=u.message.text
    if "زواج" in txt: u.message.reply_text(f"💍 تم زواج {u.effective_user.first_name} ❤️ {random.choice(['سوما','كنان','توتا'])}")
    elif "نسبه الحب" in txt or "نسبة الحب" in txt: u.message.reply_text(f"❤️ نسبة الحب {random.randint(0,100)}%")
    elif txt.startswith("صيح"):
        if u.message.reply_to_message: u.message.reply_text(u.message.reply_to_message.text)
        else: u.message.reply_text(txt.replace("صيح","").strip())
    elif txt.startswith("همس"):
        if u.message.reply_to_message:
            try: c.bot.send_message(u.message.reply_to_message.from_user.id, f"همس من {u.effective_user.first_name}: {txt.replace('همس','').strip()}"); u.message.reply_text("✅ تم ارسال الهمس")
            except: u.message.reply_text("ما اكدر اهمسله - لازم يدز للبوت ستارت")
    elif txt=="فحص": u.message.reply_text("✅ البوت شغال 100%\n⚡️ كنان بوت")
    elif txt=="كشف" and u.message.reply_to_message:
        usr=u.message.reply_to_message.from_user
        u.message.reply_text(f"كشف: {usr.first_name}\nايدي: {usr.id}\nيوزر: @{usr.username or 'لا يوجد'}")

def start(u,c): u.message.reply_text("✅ بوت كنان شغال - اكتب تفعيل")

updater=Updater(TOKEN, use_context=True)
dp=updater.dispatcher
dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.regex("^تفعيل$"), activate))
dp.add_handler(MessageHandler(Filters.regex("^تعطيل$"), deactivate))
dp.add_handler(MessageHandler(Filters.regex("^(ايدي|id)$"), id_cmd))
dp.add_handler(MessageHandler(Filters.regex("^قفل"), lock))
dp.add_handler(MessageHandler(Filters.regex("^فتح"), unlock))
dp.add_handler(MessageHandler(Filters.regex("^اضف رد"), add_reply))
dp.add_handler(MessageHandler(Filters.regex("^(حذف رد|مسح رد)"), del_reply))
dp.add_handler(MessageHandler(Filters.regex("^(حظر|طرد)$"), ban))
dp.add_handler(MessageHandler(Filters.regex("^رفع مشرف$"), lambda u,c: promote(u,c,"مشرف")))
dp.add_handler(MessageHandler(Filters.regex("^رفع ادمن$"), lambda u,c: promote(u,c,"ادمن")))
dp.add_handler(MessageHandler(Filters.regex("^رفع مميز$"), lambda u,c: promote(u,c,"مميز")))
dp.add_handler(MessageHandler(Filters.regex("^(زواج|نسبه الحب|نسبة الحب|صيح|همس|فحص|كشف)"), fun))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle))

print("Running...")
updater.start_polling()
updater.idle()
