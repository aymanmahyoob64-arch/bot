import asyncio
try: asyncio.set_event_loop(asyncio.new_event_loop())
except: pass
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import Application, MessageHandler, filters, CommandHandler, CallbackQueryHandler
import uuid, os
from datetime import timedelta
TOKEN=os.getenv("BOT_TOKEN","8945658707:AAFDNZVmjGkwGxXVqPABnKw_T97Qx_-2vIk")
pending={}; hams={}
DEV=8149673627
BAD=["كس","طيز","زب","منيك","قحبة","شرموطة","نيك","fuck","porn","sex"]
async def start(u,c):
 if c.args and c.args[0].startswith("wh_"):
  pid=c.args[0].replace("wh_",""); p=pending.get(pid)
  if p: c.user_data["w"]=pid; await u.message.reply_text(f"ارسل همستك لـ {p['to_name']}:")
async def priv(u,c):
 if "w" in c.user_data:
  pid=c.user_data["w"]; p=pending.get(pid)
  if not p: return
  hid=str(uuid.uuid4())[:8]
  hams[hid]={"to_id":p["to_id"],"from_id":p["from_id"],"text":u.message.text}
  kb=InlineKeyboardMarkup([[InlineKeyboardButton("👁 رؤية الهمسة", callback_data=f"hams_{hid}")]])
  await c.bot.send_message(p["chat_id"], f"🔒 همسة سرية", reply_markup=kb)
  await u.message.reply_text("تم ✅")
  del pending[pid]; del c.user_data["w"]
async def handle_cb(u,c):
 q=u.callback_query; hid=q.data.replace("hams_",""); h=hams.get(hid)
 if not h: await q.answer("انتهت", show_alert=True); return
 if q.from_user.id not in [h["to_id"],h["from_id"]]: await q.answer("لا تخصك", show_alert=True); return
 await q.answer(h["text"][:200], show_alert=True)
async def group(u,c):
 if not u.message or u.effective_chat.type=="private": return
 cid=str(u.effective_chat.id); uid=str(u.effective_user.id)
 txt=(u.message.text or u.message.caption or "").strip()
 if str(uid)!=str(DEV):
  if u.message.photo or u.message.video or u.message.video_note or u.message.animation or u.message.sticker:
   try: await c.bot.delete_message(int(cid), u.message.message_id)
   except: pass
   return
  if txt and any(w in txt.lower() for w in BAD):
   try:
    await c.bot.delete_message(int(cid), u.message.message_id)
    await c.bot.restrict_chat_member(int(cid), int(uid), ChatPermissions(can_send_messages=False), until_date=timedelta(hours=1))
   except: pass
   return
 if txt.lower() in ["ايدي","ا","id"]: await u.message.reply_text(f"ID:{uid}", reply_to_message_id=u.message.message_id)
 if txt.lower() in ["ه","همس"] and u.message.reply_to_message:
  t=u.message.reply_to_message.from_user
  if t.id==u.effective_user.id or t.is_bot: return
  pid=str(uuid.uuid4())[:8]
  pending[pid]={"to_id":t.id,"to_name":t.first_name,"from_id":u.effective_user.id,"from_name":u.effective_user.first_name,"chat_id":int(cid)}
  me=await c.bot.get_me()
  kb=InlineKeyboardMarkup([[InlineKeyboardButton("🔏 اهمس هنا", url=f"https://t.me/{me.username}?start=wh_{pid}")]])
  await u.message.reply_text(f"همس لـ {t.first_name}", reply_markup=kb)
app=Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, priv))
app.add_handler(CallbackQueryHandler(handle_cb))
app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, group))
print("BOT READY")
app.run_polling()
