const TelegramBot = require('node-telegram-bot-api');
const express = require('express');
const app = express();

// Render يحتاج هذا البورت
const PORT = process.env.PORT || 10000;
app.get('/', (req,res)=> res.send('Bot is Alive'));
app.listen(PORT, ()=> console.log('Web OK on port ' + PORT));

const token = process.env.BOT_TOKEN;
if(!token){ 
  console.log('BOT_TOKEN missing! Add it in Render Environment');
  process.exit(1);
}

const bot = new TelegramBot(token, {polling: true});
console.log('BOT STARTED');

bot.onText(/\/start/, (msg)=>{
  bot.sendMessage(msg.chat.id, `هلا ${msg.from.first_name} 👑\nالبوت شغال تمام!`, {
    reply_markup: {
      keyboard: [['هلا','كيفك'],['/help']],
      resize_keyboard: true
    }
  });
});

bot.onText(/\/help/, (msg)=>{
  bot.sendMessage(msg.chat.id, 'الأوامر:\n/start - البداية\n/help - المساعدة');
});

bot.on('message', (msg)=>{
  if(!msg.text) return;
  if(msg.text.startsWith('/')) return;
  const t = msg.text.toLowerCase();
  if(t.includes('هلا')) bot.sendMessage(msg.chat.id, 'هلا والله 😍');
  else if(t.includes('كيفك')) bot.sendMessage(msg.chat.id, 'بخير وانت؟ ❤️');
});
