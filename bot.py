import os, threading, time
from flask import Flask
import telebot
from telebot import types

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "kenan262_bot is Live!"

# يمنع خطأ 409
try:
    bot.remove_webhook()
    time.sleep(1)
    bot.delete_webhook(drop_pending_updates=True)
except:
    pass

whispers = {}

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "✅ بوت كنان262 شغال\n\nرد على اي رسالة واكتب! حتى تهمس")

@bot.message_handler(func=lambda m: m.text and m.text.strip() == "!" and m.reply_to_message)
def trigger(m):
    target = m.reply_to_message.from_user
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✍️ اكتب همستك", switch_inline_query_current_chat=f"to:{target.id}:{target.first_name} "))
    bot.send_message(m.chat.id, f"💌 همسة لـ {target.first_name} 👇", reply_markup=markup)

@bot.inline_handler(lambda q: True)
def inline(q):
    try:
        if not q.query.startswith("to:"):
            return
        parts = q.query.split(":", 2)
        to_id = int(parts[1])
        text = parts[2] if len(parts) > 2 else ""
        if not text.strip():
            text = "همسة سرية"
        wid = f"{q.from_user.id}_{to_id}_{q.id[-5:]}"
        whispers[wid] = {"text": text, "from_name": q.from_user.first_name, "to": to_id, "from_id": q.from_user.id}

        result = types.InlineQueryResultArticle(
            id=wid,
            title="📩 ارسل الهمسة",
            description=text[:50],
            input_message_content=types.InputTextMessageContent("🔒 همسة سرية - اضغط لاظهارها"),
            reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("👁️ اظهار الهمسة", callback_data=f"show_{wid}"))
        )
        bot.answer_inline_query(q.id, [result], cache_time=0, is_personal=True)
    except Exception as e:
        print(e)

@bot.callback_query_handler(func=lambda c: c.data.startswith("show_"))
def show(c):
    wid = c.data[5:]
    data = whispers.get(wid)
    if not data:
        bot.answer_callback_query(c.id, "انتهت صلاحية الهمسة", show_alert=True)
        return
    if c.from_user.id!= data["to"] and c.from_user.id!= data["from_id"]:
        bot.answer_callback_query(c.id, "⛔ هاي الهمسة مو الك!", show_alert=True)
        return
    bot.edit_message_text(f"💌 همسة من {data['from_name']}:\n\n{data['text']}", c.message.chat.id, c.message.message_id)
    bot.answer_callback_query(c.id, "تم ✅")

def run_bot():
    print("=== BOT kenan262_bot STARTED ===")
    while True:
        try:
            bot.infinity_polling(skip_pending=True, timeout=30, long_polling_timeout=30)
        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(5)

threading.Thread(target=run_bot).start()
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
