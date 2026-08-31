const TelegramBot = require('node-telegram-bot-api');
const express = require('express');
const app = express();
app.get('/', (req,res)=> res.send('Bot is Running - Best Bot by Ayman'));
app.listen(10000, ()=> console.log('Web server running'));

const bot = new TelegramBot(process.env.BOT_TOKEN, {polling: true});
console.log('🔥 BEST BOT STARTED 🔥');

let settings = { lockLinks: false, lockSpam: true, welcome: true }
const autoReplies = {
  'السلام عليكم': 'وعليكم السلام ورحمة الله وبركاته نورت ❤️',
  'هلا': 'هلا هلا والله بالقمر 😍👑',
  'كيفك': 'أنا بخير دامك بخير ❤️ انت كيفك؟',
  'بوت': 'عيون البوت 😎 تأمر؟',
  'بحبك': 'وأنا أموت فيك أكثر 😘❤️',
  'ضحكني': 'مرة واحد محشش سألوه وش اسمك؟ قال اسمي مكتوب في البطاقة 😂',
  'صباح الخير': 'صباح الجمال على عيونك ☀️❤️',
  'تصبح على خير': 'وانت من أهل الخير يا قلبي 🌙💤'
};

// لوحة البداية الفخمة
bot.onText(/\/start/, (msg) => {
  const name = msg.from.first_name;
  bot.sendMessage(msg.chat.id, `👑 أهلا يا ${name} 

أنا **أفضل بوت في تليجرام** 🚀
صنع بواسطة أيمن - Kenan

⚡️ سريع - ذكي - يحمي قروبك 24 ساعة

اختر من القائمة تحت:`, {
    parse_mode: 'Markdown',
    reply_markup: {
      inline_keyboard: [
        [{text: '⚙️ أوامر الإدارة', callback_data: 'admin_help'}, {text: '🔒 الحماية', callback_data: 'lock_help'}],
        [{text: '🎮 الألعاب و الترفيه', callback_data: 'games'}, {text: '💬 الردود التلقائية', callback_data: 'replies'}],
        [{text: '🎵 اغاني - فيديو', callback_data: 'media'}, {text: '🆔 معلوماتي', callback_data: 'myinfo'}],
        [{text: '➕ ضفني لقروبك', url: `https://t.me/${(await bot.getMe()).username}?startgroup=new`}]
      ]
    }
  });
});

bot.on('callback_query', async (q) => {
  const chatId = q.message.chat.id;
  if(q.data === 'admin_help'){
    bot.sendMessage(chatId, `⚙️
