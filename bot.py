import os, threading, time
from flask import Flask
import telebot
from telebot import types

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")
app = Flask(__name__)
@app.route('/')
def home(): return "Bot Kenan is live!"

# اهم سطر يمنع 409 - يمسح اي Webhook عالق
try:
    bot.remove_webhook()
    time.sleep(1)
    bot.delete_webhook(drop_pending_updates=True)
except: pass

whispers = {}
@bot.message_handler(commands=['start','الاوامر'])
def menu(m):
    markup=types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💬 كيف اهمس؟",callback_data="hms"))
    bot.send_message(m.chat.id,"✨ **بوت كنان شغال** ✨\nللهمس رد على رسالة واكتب `!`",reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data=="hms")
def hms_cb(c): bot.answer_callback_query(c.id,"رد على رسالة الشخص واكتب!",show_alert=True)

@bot.message_handler(func=lambda m: m.text and m.text.strip()=="!" and m.reply_to_message)
def trig(m):
    t=m.reply_to_message.from_user
    mk=types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("✍️ اكتب همستك",switch_inline_query_current_chat=f"to:{t.id}:{t.first_name} "))
    bot.send_message(m.chat.id,f"همسة لـ {t.first_name} 👆",reply_markup=mk)

@bot.inline_handler(lambda q: True)
def iq(q):
    try:
        if not q.query.startswith("to:"): return
        p=q.query.split(":",2); tid=int(p[1]); txt=p[2] if len(p)>2 else "همسة"
        wid=f"{q.from_user.id}_{tid}_{q.id[-4:]}"
        whispers[wid]={"text":txt,"from":q.from_user.first_name,"to":tid}
        r=types.InlineQueryResultArticle(id=wid,title="📩 ارسل همسة",description=txt[:30],input_message_content=types.InputTextMessageContent("🔒 همسة سرية - اضغط لاظهارها"),reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("👁️ اظهار الهمسة",callback_data=f"show_{wid}")))
        bot.answer_inline_query(q.id,[r],cache_time=0,is_personal=True)
    except: pass

@bot.callback_query_handler(func=lambda c: c.data.startswith("show_"))
def show(c):
    wid=c.data[5:]; d=whispers.get(wid)
    if not d: bot.answer_callback_query(c.id,"انتهت",show_alert=True); return
    if c.from_user.id!=d["to"] and c.from_user.id!=int(wid.split("_")[0]): bot.answer_callback_query(c.id,"⛔ مو الك!",show_alert=True); return
    bot.edit_message_text(f"💌 من {d['from']}:\n\n{d['text']}",c.message.chat.id,c.message.message_id)
    bot.answer_callback_query(c.id)

def run():
    print("=== BOT KENAN STARTED ===")
    while True:
        try: bot.infinity_polling(skip_pending=True, timeout=30)
        except Exception as e:
            print(f"Polling error: {e} - retry in 5s")
            time.sleep(5)

threading.Thread(target=run).start()
app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
