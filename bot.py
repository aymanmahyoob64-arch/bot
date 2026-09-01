import os, threading, json, asyncio
from flask import Flask
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

TOKEN = os.getenv("BOT_TOKEN")
print(f"TOKEN exists: {bool(TOKEN)}", flush=True)

flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "OK - Kenan Bot Live"

def run_flask():
    flask_app.run(host="0.0.0.0", port=int(os.getenv("PORT",10000)))

threading.Thread(target=run_flask, daemon=True).start()

DB="groups.json"
def load():
    if not os.path.exists(DB): return {}
    try: return json.load(open(DB,encoding='utf-8'))
    except: return {}
def save(d): json.dump(d,open(DB,'w',encoding='utf-8'),ensure_ascii=False,indent=2)

async def is_admin(u):
    try:
        m=await u.effective_chat.get_member(u.effective_user.id)
        return m.status in ['administrator','creator']
    except: return False

async def start_cmd(u,c):
    await u.message.reply_text("هلا بيك 👋 ضيفني لجروب وارفعني ادمن ودز تفعيل")

async def welcome(u,c):
    db=load(); gid=str(u.effective_chat.id)
    if gid in db and db[gid].get("active"):
        for x in u.message.new_chat_members:
            if not x.is_bot:
                await u.message.reply_text(f"هلا {x.first_name} ❤️")

async def handle(u,c):
    if not u.message or not u.message.text: return
    txt=u.message.text.strip(); gid=str(u.effective_chat.id)
    if u.effective_chat.type=='private': return
    db=load()
    if gid not in db: db[gid]={"active":False,"locks":{"link":False},"muted":[]}
    admin=await is_admin(u)

    if txt=="تفعيل":
        if not admin:
            await u.message.reply_text("للمشرفين فقط"); return
        db[gid]["active"]=True; save(db)
        await u.message.reply_text(f"تم تفعيل {u.effective_chat.title} ✅"); return

    if txt=="تعطيل" and admin:
        db[gid]["active"]=False; save(db)
        await u.message.reply_text("تم التعطيل"); return

    if not db.get(gid,{}).get("active"): return

    if txt in ["اوامري","الاوامر"]:
        await u.message.reply_text("اوامري:\nتفعيل/تعطيل\nقفل الروابط/فتح الروابط\nكتم رد/الغاء كتم رد\nايدي"); return
    if txt=="قفل الروابط" and admin:
        db[gid]["locks"]["link"]=True; save(db)
        await u.message.reply_text("تم قفل الروابط 🔒"); return
    if txt=="فتح الروابط" and admin:
        db[gid]["locks"]["link"]=False; save(db)
        await u.message.reply_text("تم فتح الروابط 🔓"); return

async def main():
    bot = Bot(TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    print("Webhook deleted", flush=True)

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("Bot Started - Kenan Live ✅", flush=True)
    await app.run_polling(drop_pending_updates=True, allowed_updates=["message","chat_member"])

if __name__=="__main__":
    asyncio.run(main())
