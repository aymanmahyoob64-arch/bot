import os, json, threading
from flask import Flask
import telebot
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running..."

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
threading.Thread(target=run_flask).start()

DATA_FILE = "data.json"
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def add_watermark(photo_bytes, text="Kenan♛"):
    img = Image.open(BytesIO(photo_bytes)).convert("RGBA")
    w, h = img.size
    overlay = Image.new("RGBA", img.size, (0,0,0,0))
    draw = ImageDraw.Draw(overlay)
    # شريط شفاف اسفل الصورة
    draw.rectangle([(0, h-80), (w, h)], fill=(0,0,0,120))
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except:
        font = ImageFont.load_default()
    # كتابة اسم مالك الجروب شفاف
    draw.text((15, h-55), text, font=font, fill=(255,255,255,200))
    final = Image.alpha_composite(img, overlay).convert("RGB")
    bio = BytesIO()
    bio.name = "id.jpg"
    final.save(bio, "JPEG")
    bio.seek(0)
    return bio

@bot.message_handler(content_types=['new_chat_members'])
def welcome(m):
    bot.send_message(m.chat.id, "نورتوا احبك 💛")

@bot.message_handler(func=lambda m: m.text and m.text.strip() in ["تفعيل","تفعيل الايدي","تفعيل الكروب"])
def activate(m):
    if m.chat.type in ['group','supergroup']:
        data = load_data()
        data[str(m.chat.id)] = {"active": True}
        save_data(data)
        bot.reply_to(m, "✅ تم تفعيل المجموعة احبك.")

@bot.message_handler(func=lambda m: True)
def count_msg(m):
    if m.chat.type not in ['group','supergroup']:
        return
    data = load_data()
    chat_id = str(m.chat.id)
    user_id = str(m.from_user.id)
    if chat_id not in data:
        data[chat_id] = {}
    if "msgs" not in data[chat_id]:
        data[chat_id]["msgs"] = {}
    if user_id not in data[chat_id]["msgs"]:
        data[chat_id]["msgs"][user_id] = 0
    data[chat_id]["msgs"][user_id] += 1
    save_data(data)

@bot.message_handler(func=lambda m: m.text and m.text.strip() in ["ا","ايدي","id","الايدي"])
def my_id(m):
    data = load_data()
    chat_id = str(m.chat.id)
    user_id = str(m.from_user.id)

    count = 0
    if chat_id in data and "msgs" in data[chat_id] and user_id in data[chat_id]["msgs"]:
        count = data[chat_id]["msgs"][user_id]

    # الرتبة
    rank = "عضو"
    try:
        member = bot.get_chat_member(m.chat.id, m.from_user.id)
        if member.status == "creator":
            rank = "المالك الاساسي"
        elif member.status == "administrator":
            rank = "ادمن"
    except:
        pass

    username = f"@{m.from_user.username}" if m.from_user.username else "لايوجد"
    title = "المالك"
    owner_name = "Kenan♛" # هنا اسم العلامة الشفافة - غيره لاسمك

    caption = f"جبر لقلبي قبل قلوبهم 💛.\n\n- NAME : {m.from_user.first_name} 𓅓.\n- UsEr : {username} 𓅓.\n- MsG : {count} متوسط 𓅓.\n- StA : {rank} 𓅓.\n- ID : {m.from_user.id} 𓅓.\n- TITLE {title} 𓅓.\n- BIO I don't need to impress you. 𓆩 𓅓."

    try:
        photos = bot.get_user_profile_photos(m.from_user.id, limit=1)
        if photos.total_count > 0:
            file_id = photos.photos[0][0].file_id
            file_info = bot.get_file(file_id)
            downloaded = bot.download_file(file_info.file_path)

            # اضافة العلامة الشفافة
            watermarked = add_watermark(downloaded, owner_name)

            bot.send_photo(m.chat.id, watermarked, caption=caption, reply_to_message_id=m.message_id)
        else:
            bot.reply_to(m, caption)
    except Exception as e:
        print(e)
        bot.reply_to(m, caption)

print("Bot is running...")
bot.infinity_polling()
