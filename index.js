const TelegramBot = require('node-telegram-bot-api');
const express = require('express');
const app = express();
app.get('/', (req,res)=> res.send('Bot is Alive'));
app.listen(10000, ()=> console.log('Web OK'));

const token = process.env.BOT_TOKEN;
if(!token){
  console.log('ERROR: BOT_TOKEN not found!');
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
  bot.sendMessage(msg.chat.id, 'الأوامر:\n/start - البداية\n/help - المساعدة\nجرب تكتب: هلا');
});

bot.on('message', (msg)=>{
  if(!msg.text) return;
  if(msg.text.startsWith('/')) return;
  let t = msg.text.toLowerCase();
  if(t.includes('هلا')) bot.sendMessage(msg.chat.id, 'هلا والله 😍');
  else if(t.includes('كيفك')) bot.sendMessage(msg.chat.id, 'بخير وانت؟ ❤️');
});
