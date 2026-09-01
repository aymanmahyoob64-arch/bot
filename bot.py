import os, json, threading, uuid
from flask import Flask
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent
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

# خزن الهمسات
whispers = {}
pending_whisper = {} # requester_id -> target_id

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
    bio = BytesIO(); bio.name="id.jpg"
    final.save(bio, "JPEG"); bio.seek(0)
    return bio

@bot.message_handler(func=lambda m: m.text and m.text.strip() in ["تفعيل","تفعيل الايدي"])
def activate(m):
    data=load_data(); chat=str(m.chat.id)
    if chat not in data: data[chat]={}
    data[chat]["active"]=True
    if "msgs" not in data[chat]: data[chat]["msgs"]={}
    save_data(data)
    bot.reply_to(m, "✅ تم تفعيل المجموعة احبك.")

def get_awamer_text():
    return "- أهلاً بك عزيزي في قائمة الاوامر :\n——————————————\n◂ م1 : اوامر الادمنيه\n◂ م2 : اوامر الاعدادات\n◂ م3 : اوامر القفل - الفتح\n◂ م4 : اوامر التسليه\n◂ م5 : اوامر Dev\n◂ م6 : الاوامر الخدميه\n——————————————"

def main_menu_markup():
    markup = InlineKeyboardMarkup(row_width=3)
    markup.add(InlineKeyboardButton("❶", callback_data="m1"), InlineKeyboardButton("❷", callback_data="m2"), InlineKeyboardButton("❸", callback_data="m3"))
    markup.add(InlineKeyboardButton("اوامر Dev", callback_data="m5"), InlineKeyboardButton("اوامر التسليه", callback_data="m4"))
    markup.add(InlineKeyboardButton("اوامر خدميه", callback_data="m6"))
    markup.add(InlineKeyboardButton("القفل والفتح", callback_data="m3_lock"), InlineKeyboardButton("التفعيل والتعطيل", callback_data="show_himaya"))
    return markup

@bot.message_handler(func=lambda m: m.text and "الاوامر" in m.text)
def awamer(m):
    bot.send_message(m.chat.id, get_awamer_text(), reply_markup=main_menu_markup())

@bot.message_handler(func=lambda m: m.text and "الحمايه" in m.text)
def himaya_cmd(m):
    show_himaya_menu(m.chat.id, None)

def show_himaya_menu(chat_id, message_id=None):
    text = "• اوامر التفعيل والتعطيل"
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("تعطيل الرابط", callback_data="x"), InlineKeyboardButton("تفعيل الرابط", callback_data="x"))
    markup.add(InlineKeyboardButton("تعطيل الترحيب", callback_data="x"), InlineKeyboardButton("تفعيل الترحيب", callback_data="x"))
    markup.add(InlineKeyboardButton("القائمه الرئيسيه", callback_data="main"), InlineKeyboardButton("اخفاء الامر", callback_data="hide"))
    if message_id:
        try: bot.edit_message_text(text, chat_id, message_id, reply_markup=markup)
        except: bot.send_message(chat_id, text, reply_markup=markup)
    else:
        bot.send_message(chat_id, text, reply_markup=markup)

MENUS = {
"m1": "• اوامر الادمنيه\n• حظر - الغاء حظر - كتم - الغاء كتم\n• طرد - تثبيت - الغاء تثبيت\n• رفع ادمن - تنزيل ادمن",
"m2": "• اوامر الاعدادات\n• وضع ترحيب - مسح الترحيب\n• وضع قوانين - مسح القوانين\n• وضع رابط - مسح الرابط",
"m3": "• اوامر القفل والفتح\n• قفل الرابط - فتح الرابط\n• قفل التاك - فتح التاك\n• قفل البوتات - فتح البوتات",
"m3_lock": "• اوامر القفل والفتح\n• قفل الرابط - فتح الرابط\n• قفل التاك - فتح التاك\n• قفل البوتات - فتح البوتات",
"m4": "• اوامر التسليه\n• زخرفه - اغنيه - افلام\n• صراحه - كت تويت",
"m5": "• اوامر Dev\n• تفعيل - تعطيل\n• اذاعه - مغادره",
"m6": "• الاوامر الخدميه\n• ايدي - رسائلي - جهاتي - سحكاتي\n• همس - كشف - الرابط"
}

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    data = call.data
    try:
        if data == "hide":
            bot.delete_message(call.message.chat.id, call.message.message_id)
            return
        if data == "main":
            bot.edit_message_text(get_awamer_text(), call.message.chat.id, call.message.message_id, reply_markup=main_menu_markup())
            return
        if data == "show_himaya":
            show_himaya_menu(call.message.chat.id, call.message.message_id)
            return
        if data in MENUS:
            txt = MENUS[data]
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("القائمه الرئيسيه", callback_data="main"))
            markup.add(InlineKeyboardButton("اخفاء الاوامر", callback_data="hide"))
            bot.edit_message_text(txt, call.message.chat.id, call.message.message_id, reply_markup=markup)
            return
        if data.startswith("show_whisper_"):
            wid = data.split("show_whisper_")[1]
            w = whispers.get(wid)
            if not w:
                bot.answer_callback_query(call.id, "انتهت صلاحية الهمسه", show_alert=True)
                return
            if call.from_user.id!= w['to_id'] and call.from_user.id!= w['from_id']:
                bot.answer_callback_query(call.id, "الهمسه مو الك 💔", show_alert=True)
                return
            bot.answer_callback_query(call.id, f"الهمسه: {w['text']}", show_alert=True)
            return
    except Exception as e:
        print(e)
    try: bot.answer_callback_query(call.id)
    except: pass

# ===== نظام الهمس مثل SOMA =====
@bot.message_handler(func=lambda m: m.reply_to_message and m.text and m.text.strip() in ["!", "همس", "هـ", "hms", "Hms"])
def hms_request(m):
    target = m.reply_to_message.from_user
    if target.id == m.from_user.id:
        bot.reply_to(m, "ما تكدر تهمس لنفسك")
        return
    # خزن الطلب
    pending_whisper[m.from_user.id] = target.id

    text = f"• تم تحديد الهمسه لـ {target.first_name} ← 👑{target.first_name}\n• اضغط الزر لكتابة الهمسة"
    markup = InlineKeyboardMarkup()
    # هذا الزر يفتح الانلاين
    markup.add(InlineKeyboardButton("اهمس هنا ↗️", switch_inline_query=f"to_{target.id}_"))
    bot.send_message(m.chat.id, text, reply_markup=markup)

@bot.inline_handler(func=lambda q: True)
def inline_query(q):
    text = q.query.strip()
    # اذا الكويري فارغ او يبدأ بـ to_
    if q.query.startswith("to_"):
        # المستخدم ضغط زر اهمس هنا ويريد يكتب
        try:
            target_id = int(q.query.replace("to_","").replace("_","").strip())
        except:
            target_id = 0
        result = InlineQueryResultArticle(
            id="1",
            title="اكتب همستك الان...",
            description="اكتب نص الهمسه واضغط ارسال",
            input_message_content=InputTextMessageContent(f"جاري كتابة همسه..."),
        )
        bot.answer_inline_query(q.id, [result], cache_time=0)
        return

    if not text:
        result = InlineQueryResultArticle(
            id="0",
            title="اكتب الهمسه",
            description="اكتب رسالتك ثم ارسل",
            input_message_content=InputTextMessageContent("...")
        )
        bot.answer_inline_query(q.id, [result], cache_time=0)
        return

    # انشاء همسه حقيقيه
    target_id = pending_whisper.get(q.from_user.id, 0)
    wid = str(uuid.uuid4())[:8]
    whispers[wid] = {
        'from_id': q.from_user.id,
        'to_id': target_id,
        'text': text,
        'from_name': q.from_user.first_name
    }
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(f"عرض الهمسه 🔒", callback_data=f"show_whisper_{wid}"))

    result = InlineQueryResultArticle(
        id=wid,
        title=f"همسه الى {target_id}",
        description=text,
        input_message_content=InputTextMessageContent(f"• همسه من {q.from_user.first_name} الى مستخدم مجهول 👇", reply_markup=markup),
        reply_markup=markup
    )
    bot.answer_inline_query(q.id, [result], cache_time=0, is_personal=True)

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
    caption = f"جبر لقلبي قبل قلوبهم 💛.\n\n- NAME : {m.from_user.first_name} ♛ 𓅓.\n- UsEr : {username} 𓅓.\n- MsG : {count} متوسط 𓅓.\n- StA : {rank} 𓅓.\n- ID : {m.from_user.id} 𓅓."
    try:
        photos=bot.get_user_profile_photos(m.from_user.id, limit=1)
        if photos.total_count>0:
            down=bot.download_file(bot.get_file(photos.photos[0][0].file_id).file_path)
            wm=add_watermark(down, "Kenan♛")
            bot.send_photo(m.chat.id, wm, caption=caption, reply_to_message_id=m.message_id)
        else:
            bot.reply_to(m, caption)
    except: bot.reply_to(m, caption)

@bot.message_handler(func=lambda m: True, content_types=['text'])
def counter(m):
    if m.chat.type not in ['group','supergroup']: return
    if m.text and any(x in m.text for x in ["الاوامر","الحمايه","تفعيل","ا "]): return
    data=load_data(); c=str(m.chat.id); u=str(m.from_user.id)
    if c not in data: data[c]={"msgs":{}}
    if "msgs" not in data[c]: data[c]["msgs"]={}
    data[c]["msgs"][u]=data[c]["msgs"].get(u,0)+1
    save_data(data)

print("Bot is running...")
bot.infinity_polling()
