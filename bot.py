import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters

TOKEN = os.getenv("BOT_TOKEN")

async def start(update, context):
    await update.message.reply_text("هلا! البوت شغال ✅")

async def echo(update, context):
    await update.message.reply_text(f"وصلتني رسالتك: {update.message.text}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    print("Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()
