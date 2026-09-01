import os
import threading
from flask import Flask
import telebot
from telebot import types

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

app = Flask(__name__)
@app.route('/')
def home(): return "Bot Kenan is live!"

whispers = {}

@bot.message_handler(commands=['start','الاوامر'])
def send_menu(m):
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        types.InlineKeyboardButton("👥 الادمنية", callback_data="admins"),
        types.InlineKeyboardButton("🔗 الرابط", callback_data="link"),
        types.InlineKeyboardButton("📌 تثبيت", callback_data="pin")
    )
    markup.add(
        types.InlineKeyboardButton("❓ المساعدة", callback_data="help"),
        types.InlineKeyboardButton("💬 الهمس", callback_data="hms_info")
    )
    bot.send_message(m.chat.id, "✨ **قائمة اوامر بوت كنان** ✨\nاختار من الازرار:", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    if c.data == "admins":
        try:
            admins = bot.get_chat_administrators(c.message.chat.id)
            txt = "👑 **الادمنية:**\n" + "\n".join([f"• {a.user.first_name}" for a in admins])
        except: txt = "ما اكدر اجيب الادمنية"
        bot.edit_message_text(txt, c.message.chat.id, c.message.message_id, reply_markup=c.message.reply_markup)
    elif c.data == "link":
        link = bot.export_chat_invite_link(c.message.chat.id)
        bot.edit_message_text(f"🔗 **رابط الجروب:**\n{link}", c.message.chat.id, c.message.message_id, reply_markup=c.message.reply_markup)
    elif c.data == "hms_info":
        bot.edit_message_text("💬 **للهمس:** رد على رسالة الشخص واكتب `!`", c.message.chat.id, c.message.message_id, reply_markup=c.message.reply_markup)
    else:
        bot.answer_callback_query(c.id, "قريبا")
    bot.answer_callback_query(c.id)

@bot.message_handler(func=lambda m: m.text and m.text.strip() == "!" and m.reply_to_message)
def whisper_trigger(m):
    target = m.reply_to_message.from_user
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✍️ اهمس هنا ↗️", switch_inline_query_current_chat=f"to:{target.id}:{target.first_name} "))
    bot.send_message(m.chat.id, f"• تم تحديد الهمسه لـ {target.first_name} 👑\n• اضغط الزر لكتابة الهمسة", reply_markup=markup)

@bot.inline_handler(lambda q: True)
def inline_q(inline_query):
    try:
        text = inline_query.query
        if not text.startswith("to:"): return
        parts = text.split(":", 2)
        target_id = int(parts[1])
        whisper_text = parts[2] if len(parts) > 2 else ""
        if not whisper_text.strip(): whisper_text = "همسة فارغة"
        wh_id = f"{inline_query.from_user.id}_{target_id}_{inline_query.id[-5:]}"
        whispers[wh_id] = {"text": whisper_text, "from": inline_query.from_user.first_name, "to": target_id}
        r = types.InlineQueryResultArticle(
            id=wh_id, title="📩 همس جديد", description=f"لـ {parts[1]}",
            input_message_content=types.InputTextMessageContent(f"🔒 همسة سرية..."),
            reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("👁️ اضهار الهمسة", callback_data=f"show_{wh_id}"))
        )
        bot.answer_inline_query(inline_query.id, [r], cache_time=0, is_personal=True)
    except Exception as e: print(e)

@bot.callback_query_handler(func=lambda c: c.data.startswith("show_"))
def show_wh(c):
    wh_id = c.data[5:]
    data = whispers.get(wh_id)
    if not data: bot.answer_callback_query(c.id, "انتهت الهمسة", show_alert=True); return
    if c.from_user.id!= data["to"] and c.from_user.id!= int(wh_id.split("_")[0]):
        bot.answer_callback_query(c.id, "⛔ مو الك هاي الهمسة!", show_alert=True); return
    bot.edit_message_text(f"💌 **همسة من {data['from']}:**\n\n{data['text']}", c.message.chat.id, c.message.message_id)
    bot.answer_callback_query(c.id)

def run_bot():
    print("=== BOT KENAN STARTED ===")
    bot.infinity_polling()

threading.Thread(target=run_bot).start()
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
