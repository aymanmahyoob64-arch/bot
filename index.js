const TelegramBot = require('node-telegram-bot-api');
const express = require('express');
const app = express();
app.get('/', (req,res)=> res.send('Best Bot by Ayman is Live ✅'));
app.listen(10000, ()=> {});

const bot = new TelegramBot(process.env.BOT_TOKEN, {polling: true});
console.log('🔥 BEST BOT - ALL FEATURES 🔥');

let settings = { lockLinks: false, welcome: true }
const autoReplies = {
  'السلام عليكم': 'وعليكم السلام ورحمة الله وبركاته ❤️ نورت',
  'هلا': 'هلا والله بالقمر 😍',
  'كيفك': 'بخير دامك بخير ❤️',
  'بوت': 'عيون البوت تأمر؟ 🤖',
  'بحبك': 'وأنا أموت فيك 😘',
  'صباح الخير': 'صباح العسل ☀️',
  'تصبح على خير': 'وانت من اهل الخير 🌙',
  'شلونك': 'تمام الحمدلله شلونك انت؟'
};
const rulesText = `📜 قوانين القروب:
1- ممنوع الروابط
2- ممنوع السب
3- احترم الكل
4- ممنوع الخاص`;

// START FAKHMA
bot.onText(/\/start/, async (msg) => {
  const me = await bot.getMe();
  bot.sendMessage(msg.chat.id, `👑 هلا يا ${msg.from.first_name}

أنا **أفضل بوت تليجرام** 🚀
إدارة + حماية + ترفيه + اغاني

كل شي بضغطة زر 👇`, {
    parse_mode: 'Markdown',
    reply_markup: {
      inline_keyboard: [
        [{text: '⚙️ الإدارة', callback_data: 'admin'}, {text: '🔒 الحماية', callback_data: 'locks'}],
        [{text: '🎮 الترفيه', callback_data: 'games'}, {text: '🎵 ميديا', callback_data: 'media'}],
        [{text: '🆔 ايدي - معلومات', callback_data: 'idinfo'}, {text: '📜 القوانين', callback_data: 'rules'}],
        [{text: '➕ ضفني لقروبك', url: `https://t.me/${me.username}?startgroup=new`}]
      ]
    }
  });
});

bot.on('callback_query', (q)=>{
  const id = q.message.chat.id;
  if(q.data==='admin') bot.sendMessage(id, `⚙️ أوامر الإدارة (رد على الشخص):\n/ban حظر\n/unban فك حظر\n/kick طرد\n/promote رفع ادمن 👑\n/demote تنزيل ادمن\n/pin تثبيت\n/del حذف\n/info معلوماته`);
  if(q.data==='locks') bot.sendMessage(id, `🔒 الحماية:\n/lock links قفل روابط\n/unlock links فتح\n/welcome on/off تفعيل الترحيب`, {reply_markup:{inline_keyboard:[[{text:'🔒 قفل الروابط', callback_data:'lock'},{text:'🔓 فتح', callback_data:'unlock'}]]}});
  if(q.data==='games') bot.sendMessage(id, `🎮 الألعاب:\n/games - العاب\n/love اسم - نسبة حب\n/zekh اسم - زخرفة\n/tarjma نص - ترجمة`, {reply_markup:{inline_keyboard:[[{text:'حجر 🪨',callback_data:'rock'},{text:'ورقة 📄',callback_data:'paper'},{text:'مقص ✂️',callback_data:'scissors'}],[{text:'❤️ نسبة الحب',callback_data:'love'},{text:'✍️ كت تويت',callback_data:'kt'}]]}});
  if(q.data==='media') bot.sendMessage(id, `🎵 الميديا:\n/song اسم الاغنية\n/video اسم الفيديو`);
  if(q.data==='idinfo') { let u=q.from; bot.sendMessage(id, `🆔 معلوماتك:\nالاسم: ${u.first_name}\nاليوزر: @${u.username||'لا يوجد'}\nالايدي: \`${u.id}\``, {parse_mode:'Markdown'}); }
  if(q.data==='rules') bot.sendMessage(id, rulesText);
  if(q.data==='lock'){ settings.lockLinks=true; bot.sendMessage(id, 'تم قفل الروابط 🔒'); }
  if(q.data==='unlock'){ settings.lockLinks=false; bot.sendMessage(id, 'تم فتح الروابط 🔓'); }
  if(['rock','paper','scissors'].includes(q.data)){ let b=['rock','paper','scissors'][Math.floor(Math.random()*3)]; bot.sendMessage(id, `انت: ${q.data}\nانا: ${b}`); }
  if(q.data==='love') bot.sendMessage(id, `❤️ نسبة حبك اليوم: ${Math.floor(Math.random()*100)}%`);
  if(q.data==='kt'){ let l=['لو خيروك بين الفلوس والحب؟','وش اكثر شي يزعجك؟','لو ترجع بالزمن وش تغير؟','تحب الليل ولا النهار؟']; bot.sendMessage(id, `✍️ ${l[Math.floor(Math.random()*l.length)]}`); }
  bot.answerCallbackQuery(q.id);
});

// إدارة
bot.onText(/\/ban/, (m)=>{ if(m.reply_to_message){ bot.banChatMember(m.chat.id, m.reply_to_message.from.id); bot.sendMessage(m.chat.id, `🔨 تم حظر ${m.reply_to_message.from.first_name}`);} });
bot.onText(/\/kick/, (m)=>{ if(m.reply_to_message){ bot.banChatMember(m.chat.id, m.reply_to_message.from.id); setTimeout(()=>bot.unbanChatMember(m.chat.id, m.reply_to_message.from.id),800); bot.sendMessage(m.chat.id, `👢 تم طرد ${m.reply_to_message.from.first_name}`);} });
bot.onText(/\/unban/, (m)=>{ if(m.reply_to_message) { bot.unbanChatMember(m.chat.id, m.reply_to_message.from.id); bot.sendMessage(m.chat.id, '✅ تم فك الحظر'); }});
bot.onText(/\/promote/, async (m)=>{ if(m.reply_to_message){ await bot.promoteChatMember(m.chat.id, m.reply_to_message.from.id, {can_manage_chat:true, can_delete_messages:true, can_restrict_members:true, can_pin_messages:true}); bot.sendMessage(m.chat.id, `👑 تم رفع ${m.reply_to_message.from.first_name} ادمن`);} });
bot.onText(/\/demote/, async (m)=>{ if(m.reply_to_message){ await bot.promoteChatMember(m.chat.id, m.reply_to_message.from.id, {can_manage_chat:false}); bot.sendMessage(m.chat.id, 'تم تنزيله'); }});
bot.onText(/\/pin/, (m)=>{ if(m.reply_to_message) bot.pinChatMessage(m.chat.id, m.reply_to_message.message_id); });
bot.onText(/\/del/, (m)=>{ if(m.reply_to_message){ bot.deleteMessage(m.chat.id, m.reply_to_message.message_id); bot.deleteMessage(m.chat.id, m.message_id);} });
bot.onText(/\/info/, (m)=>{ let u=m.reply_to_message?m.reply_to_message.from:m.from; bot.sendMessage(m.chat.id, `🆔 ${u.first_name}\nالايدي: ${u.id}\nاليوزر: @${u.username||'لا يوجد'}`); });
bot.onText(/\/id/, (m)=>{ let u=m.reply_to_message?m.reply_to_message.from:m.from; bot.sendMessage(m.chat.id, `🆔 ايديك: ${u.id}\nاسمك: ${u.first_name}\nاليوزر: @${u.username||'لايوجد'}`); });
bot.onText(/\/القوانين/, (m)=> bot.sendMessage(m.chat.id, rulesText));
bot.onText(/\/rules/, (m)=> bot.sendMessage(m.chat.id, rulesText));

// حماية
bot.onText(/\/lock links/, (m)=>{ settings.lockLinks=true; bot.sendMessage(m.chat.id, '🔒 قفل الروابط'); });
bot.onText(/\/unlock links/, (m)=>{ settings.lockLinks=false; bot.sendMessage(m.chat.id, '🔓 فتح الروابط'); });
bot.onText(/\/welcome (on|off)/, (m,s)=>{ settings.welcome = s[1]==='on'; bot.sendMessage(m.chat.id, s[1]==='on'?'✅ تفعيل الترحيب':'❌ تعطيل الترحيب'); });

// ميديا + ترفيه
bot.onText(/\/song (.+)/, (m,s)=> bot.sendMessage(m.chat.id, `🎵 ${s[1]}\n▶️ https://www.youtube.com/results?search_query=${encodeURIComponent(s[1])}`));
bot.onText(/\/video (.+)/, (m,s)=> bot.sendMessage(m.chat.id, `🎬 ${s[1]}\n▶️ https://www.youtube.com/results?search_query=${encodeURIComponent(s[1])}`));
bot.onText(/\/love (.+)/, (m,s)=> bot.sendMessage(m.chat.id, `❤️ نسبة الحب بينك وبين ${s[1]} : ${Math.floor(Math.random()*100)}%`));
bot.onText(/\/zekh (.+)/, (m,s)=>{ let t=s[1]; bot.sendMessage(m.chat.id, `🎨 زخرفة ${t}:\n\n★彡 ${t} 彡★\n꧁༒ ${t} ༒꧂\n『 ${t} 』\n◥ ${t} ◤`); });
bot.onText(/\/tarjma (.+)/, (m,s)=> bot.sendMessage(m.chat.id, `🌐 الترجمة:\n
