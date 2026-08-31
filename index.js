
const TelegramBot = require('node-telegram-bot-api');
const bot = new TelegramBot(process.env.BOT_TOKEN, {polling: true});

console.log('Bot started - Super Bot Kenan');

// قاعدة بيانات مؤقتة
let locks = { links: false }

// /start
bot.onText(/\/start/, (msg) => {
  bot.sendMessage(msg.chat.id, `أهلا يا ${msg.from.first_name} 👋
أنا بوت كينان الخارق 🔥

الأوامر:
⚙️ الإدارة:
 /ban - حظر بالرد
 /unban - الغاء حظر بالرد
 /promote - رفع ادمن بالرد
 /demote - تنزيل ادمن بالرد
 /pin - تثبيت بالرد
 /del - حذف بالرد

🔒 الحماية:
 /lock links - قفل الروابط
 /unlock links - فتح الروابط

🎮 الترفيه:
 /games - قائمة الالعاب
 /love - نسبة الحب
 / whisper نص - همسة

🎵 الميديا:
 /song اسم الاغنية - بحث اغنية
 /video اسم الفيديو - بحث فيديو
`, {reply_to_message_id: msg.message_id});
});

// --- الإدارة ---
bot.onText(/\/ban/, (msg) => {
  if(!msg.reply_to_message) return bot.sendMessage(msg.chat.id, 'رد على الشخص عشان تحظره');
  bot.banChatMember(msg.chat.id, msg.reply_to_message.from.id);
  bot.sendMessage(msg.chat.id, `تم حظر ${msg.reply_to_message.from.first_name} ❌`);
});

bot.onText(/\/unban/, (msg) => {
  if(!msg.reply_to_message) return;
  bot.unbanChatMember(msg.chat.id, msg.reply_to_message.from.id);
  bot.sendMessage(msg.chat.id, `تم الغاء حظر ${msg.reply_to_message.from.first_name} ✅`);
});

bot.onText(/\/promote/, async (msg) => {
  if(!msg.reply_to_message) return;
  await bot.promoteChatMember(msg.chat.id, msg.reply_to_message.from.id, {can_manage_chat:true, can_delete_messages:true, can_restrict_members:true, can_pin_messages:true});
  bot.sendMessage(msg.chat.id, `تم رفع ${msg.reply_to_message.from.first_name} ادمن 👑`);
});

bot.onText(/\/demote/, async (msg) => {
  if(!msg.reply_to_message) return;
  await bot.promoteChatMember(msg.chat.id, msg.reply_to_message.from.id, {can_manage_chat:false});
  bot.sendMessage(msg.chat.id, `تم تنزيل ${msg.reply_to_message.from.first_name} من الادمنية`);
});

bot.onText(/\/pin/, (msg) => {
  if(!msg.reply_to_message) return;
  bot.pinChatMessage(msg.chat.id, msg.reply_to_message.message_id);
});

bot.onText(/\/del/, (msg) => {
  if(msg.reply_to_message){
    bot.deleteMessage(msg.chat.id, msg.reply_to_message.message_id);
    bot.deleteMessage(msg.chat.id, msg.message_id);
  }
});

// --- الحماية ---
bot.onText(/\/lock links/, (msg) => {
  locks.links = true;
  bot.sendMessage(msg.chat.id, 'تم قفل الروابط 🔒');
});
bot.onText(/\/unlock links/, (msg) => {
  locks.links = false;
  bot.sendMessage(msg.chat.id, 'تم فتح الروابط 🔓');
});

bot.on('message', (msg) => {
  if(locks.links && msg.text && (msg.text.includes('http') || msg.text.includes('t.me') || msg.text.includes('@'))){
    bot.deleteMessage(msg.chat.id, msg.message_id);
    bot.sendMessage(msg.chat.id, `يا ${msg.from.first_name} ممنوع الروابط!`);
  }
});

// --- ترفيه ---
bot.onText(/\/games/, (msg) => {
  bot.sendMessage(msg.chat.id, 'اختر لعبة:', {
    reply_markup: {
      inline_keyboard: [
        [{text: 'حجر 🪨', callback_data: 'rock'}, {text: 'ورقة 📄', callback_data: 'paper'}, {text: 'مقص ✂️', callback_data: 'scissors'}],
        [{text: 'نسبة الحب ❤️', callback_data: 'love'}]
      ]
    }
  });
});

bot.on('callback_query', (q) => {
  const games = ['rock','paper','scissors'];
  if(games.includes(q.data)){
    let botChoice = games[Math.floor(Math.random()*3)];
    bot.answerCallbackQuery(q.id, {text: `البوت اختار ${botChoice}`});
    bot.sendMessage(q.message.chat.id, `انت: ${q.data}\nالبوت: ${botChoice}`);
  }
  if(q.data === 'love'){
    let percent = Math.floor(Math.random()*100);
    bot.sendMessage(q.message.chat.id, `نسبة حبك ❤️ ${percent}%`);
  }
});

bot.onText(/\/love (.+)/, (msg, match) => {
  let percent = Math.floor(Math.random()*100);
  bot.sendMessage(msg.chat.id, `نسبة الحب بينك وبين ${match[1]} هي ${percent}% ❤️`);
});

// همسة
bot.onText(/\/whisper (.+)/, (msg, match) => {
  bot.sendMessage(msg.chat.id, `📩 همسة سرية`, {
    reply_markup: {
      inline_keyboard: [[{text: 'عرض الهمسة 👀', callback_data: `wh_${msg.from.id}_${match[1]}` }]]
    }
  });
});

// ميديا
bot.onText(/\/song (.+)/, (msg, match) => {
  let query = encodeURIComponent(match[1]);
  bot.sendMessage(msg.chat.id, `🎵 اغنيتك: ${match[1]}\nحمّلها من هنا: https://www.youtube.com/results?search_query=${query}`);
});

bot.onText(/\/video (.+)/, (msg, match) => {
  let query = encodeURIComponent(match[1]);
  bot.sendMessage(msg.chat.id, `🎬 فيديو: ${match[1]}\nhttps://www.youtube.com/results?search_query=${query}`);
});// --- ردود تلقائية ---
const autoReplies = {
  'السلام عليكم': 'وعليكم السلام ورحمة الله وبركاته ❤️',
  'هلا': 'هلا والله نورت 😍',
  'كيفك': 'الحمدلله بخير، انت كيفك؟ ❤️',
  'بوت': 'نعم؟ تأمرني؟ 🤖',
  'بحبك': 'وأنا كمان بحبك أكثر 😘',
  'تصبحون على خير': 'وانت من أهل الخير 🌙',
  'صباح الخير': 'صباح النور والسرور ☀️',
  'وينك': 'موجود معكم 🫡'
};

bot.on('message', (msg) => {
  if(!msg.text) return;
  let text = msg.text.toLowerCase().trim();
  for(let key in autoReplies){
    if(text.includes(key.toLowerCase())){
      bot.sendMessage(msg.chat.id, autoReplies[key], {reply_to_message_id: msg.message_id});
      break;
    }
  }
});
