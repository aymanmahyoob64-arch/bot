const TelegramBot = require('node-telegram-bot-api');
const express = require('express');
const app = express();
app.get('/', (req,res)=> res.send('Bot is Alive'));
app.listen(10000, ()=> console.log('Web OK'));

const token = process.env.BOT_TOKEN;
if(!token){ console.log('BOT_TOKEN missing'); process.exit(1); }

const bot = new TelegramBot(token, {polling: true});
console.log('BOT STARTED');

bot.onText(/\/start/, (msg)=>{
  bot.sendMessage(msg.chat.id, `هلا ${msg.from.first_name} 👑 البوت شغال!`, {
    reply_markup: { keyboard: [['هلا','كيفك']], resize_keyboard: true }
  });
});

bot.on('message', (msg)=>{
  if(!msg.text || msg.text.startsWith('/')) return;
  if(msg.text.includes('هلا')) bot.sendMessage(msg.chat.id, 'هلا والله 😍');
});
