import os, json, threading
from flask import Flask
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is running..."
threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))).start()

DATA_FILE = "data.json"
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f: json.dump({}, f)
def load_data():
    try:
        with open(DATA_FILE, "r") as f: return json.load(f)
    except: return {}
def save_data(d):
    with open(DATA_FILE, "w") as f: json.dump(d, f)

def add_watermark(photo_bytes, text="Kenan♛"):
    img = Image.open(BytesIO(photo_bytes)).convert("RGBA")
    w,h = img.size
    overlay = Image.new("RGBA", img.size, (0,0,0,0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle([(0, h-80), (w, h)], fill=(0,0,0,120))
    try: font = ImageFont.truetype("arial.ttf", 36)
    except: font = ImageFont.load_default()
    draw.text((15, h-55), text, font=font, fill=(255,255,255,200))
    final = Image.alpha_composite(img, overlay).convert("RGB")
    bio = BytesIO()
    bio.name = "id.jpg"
    final.save(bio, "JPEG")
    bio.seek(0)
    return bio

# 1- امر التفعيل اول شي
@bot.message_handler(func=lambda m: m.text and m.text.strip() in ["تفعيل","تفعيل الايدي"])
def activate(m):
    data=load_data()
    chat=str(m.chat.id)
    if chat not in data: data[chat]={}
    data[chat]["active"]=True
    if "msgs" not in data[chat]: data[chat]["msgs"]={}
    save_data(data)
    bot.reply_to(m, "✅ تم تفعيل المجموعة احبك.")

# 2- امر الاوامر
@bot.message_handler(func=lambda m: m.text and m.text.strip() in ["الاوامر","اوامر","ا الاوامر"])
def awamer(m):
    text = """- أهلاً بك عزيزي في قائمة الاوامر :
——————————————
◂ م1 : اوامر الادمنيه
◂ م2 : اوامر الاعدادات
◂ م3 : اوامر القفل - الفتح
◂ م4 : اوامر التسليه
◂ م5 : اوامر Dev
◂ م6 : الاوامر الخدميه
——————————————"""
    markup = InlineKeyboardMarkup(row_width=3)
    markup.add(
        InlineKeyboardButton("❶", callback_data="m1"),
        InlineKeyboardButton("❷", callback_data="m2"),
        InlineKeyboardButton("❸", callback_data="m3")
    )
    markup.add(
        InlineKeyboardButton("اوامر Dev", callback_data="m5"),
        InlineKeyboardButton("اوامر التسليه", callback_data="m4")
    )
    markup.add(InlineKeyboardButton("اوامر خدميه", callback_data="m6"))
    markup.add(
        InlineKeyboardButton("القفل والفتح", callback_data="m3"),
        InlineKeyboardButton("التفعيل والتعطيل", callback_data="show_himaya")
    )
    bot.send_message(m.chat.id, text, reply_markup=markup)

# 3- امر الحمايه الي بالصورة مالك
@bot.message_handler(func=lambda m: m.text and "الحمايه" in m.text)
def himaya(m):
    text = "• اوامر التفعيل والتعطيل"
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("تعطيل الرابط", callback_data="x"), InlineKeyboardButton("تفعيل الرابط", callback_data="x"))
    markup.add(InlineKeyboardButton("تعطيل الترحيب", callback_data="x"), InlineKeyboardButton("تفعيل الترحيب", callback_data="x"))
    markup.add(InlineKeyboardButton("تعطيل الايدي", callback_data="x"), InlineKeyboardButton("تفعيل الايدي", callback_data="x"))
    markup.add(InlineKeyboardButton("تعطيل الردود", callback_data="x"), InlineKeyboardButton("تفعيل الردود", callback_data="x"))
    markup.add(InlineKeyboardButton("تعطيل الردود العامه", callback_data="x"), InlineKeyboardButton("تفعيل الردود العامه", callback_data="x"))
    markup.add(InlineKeyboardButton("تعطيل الرفع", callback_data="x"), InlineKeyboardButton("تفعيل الرفع", callback_data="x"))
    markup.add(InlineKeyboardButton("تعطيل الطرد", callback_data="x"), InlineKeyboardButton("تفعيل الطرد", callback_data="x"))
    markup.add(InlineKeyboardButton("تعطيل الالعاب", callback_data="x"), InlineKeyboardButton("تفعيل الالعاب", callback_data="x"))
    markup.add(InlineKeyboardButton("اخفاء الامر", callback_data="hide"))
    bot.send_message(m.chat.id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    if call.data == "show_himaya":
        # نستدعي نفس قائمة الحمايه
        text = "• اوامر التفعيل والتعطيل"
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(InlineKeyboardButton("تعطيل الرابط", callback_data="x"), InlineKeyboardButton("تفعيل الرابط", callback_data="x"))
        markup.add(InlineKeyboardButton("تعطيل الترحيب", callback_data="x"), InlineKeyboardButton("تفعيل الترحيب", callback_data="x"))
        markup.add(InlineKeyboardButton("تعطيل الايدي", callback_data="x"), InlineKeyboardButton("تفعيل الايدي", callback_data="x"))
        markup.add(InlineKeyboardButton("تعطيل الردود", callback_data="x"), InlineKeyboardButton("تفعيل الردود", callback_data="x"))
        markup.add(InlineKeyboardButton("تعطيل الردود العامه", callback_data="x"), InlineKeyboardButton("تفعيل الردود العامه", callback_data="x"))
        markup.add(InlineKeyboardButton("تعطيل الرفع", callback_data="x"), InlineKeyboardButton("تفعيل الرفع", callback_data="x"))
        markup.add(InlineKeyboardButton("تعطيل الطرد", callback_data="x"), InlineKeyboardButton("تفعيل الطرد", callback_data="x"))
        markup.add(InlineKeyboardButton("تعطيل الالعاب", callback_data="x"), InlineKeyboardButton("تفعيل الالعاب", callback_data="x"))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
    elif call.data == "hide":
        bot.delete_message(call.message.chat.id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "تم ✅")

# 4- امر الايدي
@bot.message_handler(func=lambda m: m.text and m.text.strip() in ["ا","ايدي","id"])
def my_id(m):
    data=load_data()
    count = data.get(str(m.chat.id),{}).get("msgs",{}).get(str(m.from_user.id),0)
    rank="عضو"
    try:
        s=bot.get_chat_member(m.chat.id, m.from_user.id).status
        if s=="creator": rank="المالك الاساسي"
        elif s=="administrator": rank="ادمن"
    except: pass
    username = f"@{m.from_user.username}" if m.from_user.username else "لايوجد"
    owner_name = "Kenan♛"
    caption = f"جبر لقلبي قبل قلوبهم 💛.\n\n- NAME : {m.from_user.first_name} ♛ 𓅓.\n- UsEr : {username} 𓅓.\n- MsG : {count} متوسط 𓅓.\n- StA : {rank} 𓅓.\n- ID : {m.from_user.id} 𓅓.\n- TITLE المالك 𓅓.\n- BIO I don't need to impress you. 𓆩 𓅓."
    try:
        photos=bot.get_user_profile_photos(m.from_user.id, limit=1)
        if photos.total_count>0:
            f_id=photos.photos[0][0].file_id
            down=bot.download_file(bot.get_file(f_id).file_path)
            wm=add_watermark(down, owner_name)
            bot.send_photo(m.chat.id, wm, caption=caption, reply_to_message_id=m.message_id)
        else:
            bot.reply_to(m, caption)
    except Exception as e:
        print(e)
        bot.reply_to(m, caption)

# 5- عداد الرسائل يكون اخر واحد حتى ما يخرب الاوامر
@bot.message_handler(func=lambda m: True, content_types=['text'])
def counter(m):
    if m.chat.type not in ['group','supergroup']: return
    # لا تحسب اوامر
    if m.text and m.text.startswith(("ا ","تفعيل","الاوامر","الحمايه")): return
    data=load_data()
    c=str(m.chat.id); u=str(m.from_user.id)
    if c not in data: data[c]={"msgs":{}}
    if "msgs" not in data[c]: data[c]["msgs"]={}
    data[c]["msgs"][u]=data[c]["msgs"].get(u,0)+1
    save_data(data)

print("Bot is running...")
bot.infinity_polling()
