import os, threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

# سيرفر حتى Render المجاني يقبله
flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "Bot is live - Kenan"
def run_flask():
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
threading.Thread(target=run_flask, daemon=True).start()

# يرد على /start بالخاص وبالجروب
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("البوت شغال بالجروب ✅\nجرب تكتب اي شي")

# يرد على اي رسالة بالجروب
async def handle_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_type = update.effective_chat.type
    print(f"رسالة من {chat_type}: {text}") # حتى تشوفها بـ Logs
    await update.message.reply_text(f"وصلتني رسالتك: {text}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    # هذا السطر هو اللي يخليه يرد بالجروب
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all))
    print("Bot started polling...")
    app.run_polling()
