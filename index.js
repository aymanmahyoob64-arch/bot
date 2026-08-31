const TelegramBot = require('node-telegram-bot-api');
const fs = require('fs');
const express = require('express');
const app = express();
app.get('/', (req,res)=> res.send('Kenan Pro Bot ♛'));
app.listen(process.env.PORT || 10000);

const bot = new TelegramBot(process.env.BOT_TOKEN, {polling: true});
console.log('KENAN PRO STARTED ♛');

let data = { groups: {}, owners: {}, admins: {}, welcome: {} };
if(fs.existsSync('data.json')) data = JSON.parse(fs.readFileSync('data.json'));
const save = ()=> fs.writeFileSync('data.json', JSON.stringify(data));

// تفعيل احترافي نفس بوتاتهم
bot.onText(/^(تفعيل|تفعيل الجروب)$/, async (msg)=>{
  const chatId = msg.chat.id;
  if(msg.chat.type === 'private') return bot.sendMessage(chatId, 'التفعيل بالجروبات فقط');

  if(data.groups[chatId]){
    return bot.sendMessage(chatId, `• المجموعه : ${msg.chat.title}\n• تم تفعيلها مسبقا\n• بواسطة : ${msg.from.first_name} ♛`);
  }

  data.groups[chatId] = true;
  if(!data.owners[chatId]) data.owners[chatId] = [];
  if(!data.admins[chatId]) data.admins[chatId] = [];
  save();

  bot.sendMessage(chatId, `✅ تم تفعيل الجروب\n• المجموعه : ${msg.chat.title}\n• بواسطة : ${msg.from.first_name} ♛\n\nالاوامر:\nرفع مالك اساسي بالرد\nرفع ادمن بالرد\nتنزيل ادمن بالرد\nكشف بالرد\nطرد بالرد\nتثبيت بالرد`);
});

// رفع مالك اساسي
bot.onText(/^رفع مالك اساسي$/, async (msg)=>{
  const chatId = msg.chat.id;
  if(!data.groups[chatId]) return;
  if(!msg.reply_to_message) return bot.sendMessage(chatId, '• رد على رسالة الشخص');
  const member = await bot.getChatMember(chatId, msg.from.id);
  if(member.status!== 'creator') return bot.sendMessage(chatId, '• هذا الامر لمنشئ الجروب فقط');
  const target = msg.reply_to_message.from;
  if(data.owners[chatId].includes(target.id)){
    return bot.sendMessage(chatId, `• تم رفعه مالك اساسي مسبقاً\n• المستخدم ← ${target.first_name}`);
  }
  data.owners[chatId].push(target.id);
  save();
  bot.sendMessage(chatId, `• تم رفعه مالك اساسي\n• المستخدم ← ${target.first_name} ♛`);
});

// رفع ادمن حقيقي
bot.onText(/^(رفع ادمن|رفع مشرف)$/, async (msg)=>{
  const chatId = msg.chat.id;
  if(!data.groups[chatId]) return;
  if(!msg.reply_to_message) return;
  try{
    await bot.promoteChatMember(chatId, msg.reply_to_message.from.id, {
      can_delete_messages: true, can_restrict_members: true, can_pin_messages: true, can_promote_members: false, can_manage_chat: true
    });
    bot.sendMessage(chatId, `• تم رفع الادمن\n• المستخدم ← ${msg.reply_to_message.from.first_name} ♛`);
  }catch(e){ bot.sendMessage(chatId, '• البوت ليس لديه صلاحية رفع مشرفين'); }
});

// تنزيل ادمن
bot.onText(/^(تنزيل ادمن|تنزيل مشرف)$/, async (msg)=>{
  const chatId = msg.chat.id;
  if(!data.groups[chatId]) return;
  if(!msg.reply_to_message) return;
  try{
    await bot.promoteChatMember(chatId, msg.reply_to_message.from.id, {can_delete_messages:false,can_restrict_members:false,can_pin_messages:false,can_promote_members:false,can_manage_chat:false});
    bot.sendMessage(chatId, `• تم تنزيل الادمن\n• المستخدم ← ${msg.reply_to_message.from.first_name}`);
  }catch(e){}
});

// كشف
bot.onText(/^(كشف|ايدي)$/, (msg)=>{
  if(!msg.reply_to_message) return;
  const u = msg.reply_to_message.from;
  bot.sendMessage(msg.chat.id, `• الاسم : ${u.first_name}\n• الايدي : ${u.id}\n• اليوزر : @${u.username || 'لا يوجد'} ♛`);
});

// طرد
bot.onText(/^(طرد|حظر)$/, async (msg)=>{
  const chatId = msg.chat.id;
  if(!data.groups[chatId]) return;
  if(!msg.reply_to_message) return;
  try{ await bot.banChatMember(chatId, msg.reply_to_message.from.id); bot.sendMessage(chatId, `• تم طرد ${msg.reply_to_message.from.first_name}`);}catch(e){ bot.sendMessage(chatId, '• ما قدرت اطرده'); }
});

// تثبيت
bot.onText(/^تثبيت$/, (msg)=>{
  if(!msg.reply_to_message) return;
  bot.pinChatMessage(msg.chat.id, msg.reply_to_message.message_id).catch(()=>{});
  bot.sendMessage(msg.chat.id, '• تم تثبيت الرساله ♛');
});

// ترحيب
bot.on('new_chat_members', (msg)=>{
  const chatId = msg.chat.id;
  if(!data.groups[chatId]) return;
  const name = msg.new_chat_members[0].first_name;
  bot.sendMessage(chatId, `• هلا ${name} نورت ${msg.chat.title} ♛`);
});

bot.onText(/\/start/, (msg)=> bot.sendMessage(msg.chat.id, `هلا ${msg.from.first_name} ♛\nبوت Kenan الاحترافي شغال`));
