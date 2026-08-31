const TelegramBot = require('node-telegram-bot-api');
const fs = require('fs');
const express = require('express');
const app = express();
app.get('/', (req,res)=> res.send('Kenan Bot is Alive ♛'));
app.listen(process.env.PORT || 10000);

const bot = new TelegramBot(process.env.BOT_TOKEN, {polling: true});
console.log('KENAN BOT STARTED ♛');

// تخزين
let data = { groups: {}, owners: {} };
if(fs.existsSync('data.json')) data = JSON.parse(fs.readFileSync('data.json'));
const save = ()=> fs.writeFileSync('data.json', JSON.stringify(data));

function isAdmin(chatId, userId, msg){
  if(data.owners[chatId]?.includes(userId)) return true;
  return bot.getChatMember(chatId, userId).then(m=> m.status === 'creator' || m.status === 'administrator').catch(()=>false);
}

// تفعيل
bot.onText(/^(تفعيل|تفعيل الجروب)$/, async (msg)=>{
  const chatId = msg.chat.id;
  if(msg.chat.type === 'private') return;
  const check = await isAdmin(chatId, msg.from.id);
  if(!check) return bot.sendMessage(chatId, 'للمشرفين فقط!');
  data.groups[chatId] = true;
  if(!data.owners[chatId]) data.owners[chatId] = [];
  save();
  bot.sendMessage(chatId, `✅ تم تفعيل الجروب\nبواسطة: ${msg.from.first_name} ♛\n\nالاوامر:\nرفع مالك اساسي بالرد\nرفع ادمن بالرد\nتنزيل ادمن بالرد\nكشف بالرد\nطرد بالرد\nتثبيت بالرد`);
});

// رفع مالك اساسي
bot.onText(/^رفع مالك اساسي$/, async (msg)=>{
  const chatId = msg.chat.id;
  if(!data.groups[chatId]) return;
  if(!msg.reply_to_message) return bot.sendMessage(chatId, 'رد على الشخص!');
  let member = await bot.getChatMember(chatId, msg.from.id);
  if(member.status!== 'creator') return bot.sendMessage(chatId, 'لمنشئ الجروب فقط!');
  const targetId = msg.reply_to_message.from.id;
  if(data.owners[chatId].includes(targetId)) return bot.sendMessage(chatId, `• تم رفعه مالك اساسي مسبقاً\n• المستخدم ← ${msg.reply_to_message.from.first_name}`);
  data.owners[chatId].push(targetId);
  save();
  bot.sendMessage(chatId, `• تم رفع مالك اساسي\n• المستخدم ← ${msg.reply_to_message.from.first_name}`);
});

// رفع ادمن (يرفع ادمن حقيقي)
bot.onText(/^(رفع ادمن|رفع مشرف)$/, async (msg)=>{
  const chatId = msg.chat.id;
  if(!data.groups[chatId]) return bot.sendMessage(chatId, 'فعل البوت بكلمة تفعيل');
  if(!msg.reply_to_message) return bot.sendMessage(chatId, 'رد على الشخص!');
  try{
    await bot.promoteChatMember(chatId, msg.reply_to_message.from.id, {
      can_delete_messages: true, can_restrict_members: true, can_pin_messages: true, can_promote_members: false, can_manage_chat: true
    });
    bot.sendMessage(chatId, `✅ تم رفع ${msg.reply_to_message.from.first_name} ادمن ♛`);
  }catch(e){ bot.sendMessage(chatId, 'ما قدرت! خل البوت مشرف بصلاحية اضافة مشرفين'); }
});

// كشف
bot.onText(/^(كشف|ايدي)$/, (msg)=>{
  if(!msg.reply_to_message) return;
  const u = msg.reply_to_message.from;
  bot.sendMessage(msg.chat.id, `الاسم: ${u.first_name}\nالايدي: ${u.id}\nاليوزر: @${u.username || 'لا يوجد'}`);
});

// تثبيت
bot.onText(/^تثبيت$/, (msg)=>{
  if(!msg.reply_to_message) return;
  bot.pinChatMessage(msg.chat.id, msg.reply_to_message.message_id).catch(()=> bot.sendMessage(msg.chat.id, 'ما قدرت اثبت!'));
});

bot.onText(/\/start/, (msg)=> bot.sendMessage(msg.chat.id, `هلا ${msg.from.first_name} ♛\nبوت Kenan المطور شغال`));
