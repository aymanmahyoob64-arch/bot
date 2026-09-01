import asyncio
try: asyncio.set_event_loop(asyncio.new_event_loop())
except: pass
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import uuid, os
from datetime import timedelta

TOKEN=os.getenv("BOT_TOKEN")
pending={}; hams={}
DEV=8149673627
BAD=["كس","طيز","زب","منيك","قحبة","شرموطة","نيك"]

async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if c.args and c.args[0].startswith("wh_"):
        pid=c.args[0].replace("wh_",""); p=pending.get(pid)
        if p: c.user_data["w"]=pid; await u.message.reply_text("ارسل همستك الآن (خاص):")
        else: await u.message.reply_text("الرابط منتهي")
    else:
        await u.message.reply_text("ارسل رابط الهمسة: https://t.me/YourBot?start=wh_ID")

async def priv(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if "w" in c.user_data:
        pid=c.user_data["w"]; p=pending.get(pid)
        if not p: return
        hid=str(uuid.uuid4())[:8]
        hams[hid]={"to_id":p["to_id"],"from_id":p["from_id"],"text":u.message.text}
        kb=InlineKeyboardMarkup([[InlineKeyboardButton("👁️ عرض الهمسة", callback_data=f"hams_{hid}")]])
        await c.bot.send_message(p["chat_id"], f"🔒 همسة جديدة لك", reply_markup=kb)
        await u.message.reply_text("تم ✅")
        del pending[pid]; del c.user_data["w"]
    else:
        # هذا للشخص اللي يبغى يرسل همسة
        pid=str(uuid.uuid4())[:8]
        pending[pid]={"to_id":u.effective_user.id,"from_id":u.effective_user.id,"chat_id":u.effective_chat.id}
        link=f"https://t.me/{c.bot.username}?start=wh_{pid}"
        await u.message.reply_text(f"انسخ هذا الرابط وارسله:\n{link}")

async def handle_cb(u: Update, c: ContextTypes.DEFAULT_TYPE):
    q=u.callback_query; await q.answer()
    if q.data.startswith("hams_"):
        hid=q.data.replace("hams_",""); h=hams.get(hid)
        if not h: await q.edit_message_text("انتهت"); return
        if q.from_user.id!= h["to_id"] and q.from_user.id!= DEV:
            await q.answer("مو لك", show_alert=True); return
        await q.edit_message_text(f"الهمسة:\n\n{h['text']}")

def main():
    app=Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_cb))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, priv))
    print("Bot started")
    app.run_polling()

if __name__=="__main__":
    main()
