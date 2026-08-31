const TelegramBot = require('node-telegram-bot-api');
const express = require('express');
const app = express();
app.get('/', (req,res)=> res.send('Bot is Alive'));
app.listen(process.env.PORT || 10000);

const bot = new TelegramBot(process.env.BOT_TOKEN, {polling: true});
console.log('BOT STARTED');

let activeGroups = new Set();

// أمر التفعيل
bot.onText(/^(تفعيل|تفعيل الجروب)$/, async (msg)=>{
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  
  if(msg.chat.type === 'private'){
    return bot.sendMessage(chatId, 'التفعيل في الجروب فقط!');
  }

  try{
    const member = await bot.getChatMember(chatId, userId);
    if(member.status !== 'creator' && member.status !== 'administrator'){
      return bot.sendMessage(chatId, 'هذا الأمر للمشرفين فقط!');
    }

    activeGroups.add(chatId);
    bot.sendMessage(chatId, `✅ تم تفعيل الجروب\nبواسطة: ${msg.from.first_name}\n\nالأوامر:\nرفع ادمن بالرد\nتنزيل ادمن بالرد\nرفع مالك بالرد\nتثبيت + بالرد`);
  }catch(e){
    bot.sendMessage(chatId, 'البوت لازم يكون مشرف!');
  }
});

// رفع ادمن
bot.onText(/^(رفع ادمن|رفع مشرف)$/, async (msg)=>{
  const chatId = msg.chat.id;
  if(!activeGroups.has(chatId)) return bot.sendMessage(chatId, 'فعل البوت أولا بكلمة تفعيل');
  if(!msg.reply_to_message) return bot.sendMessage(chatId, 'رد على رسالة الشخص!');

  try{
    const targetId = msg.reply_to_message.from.id;
    await bot.promoteChatMember(chatId, targetId, {
      can_delete_messages: true,
      can_restrict_members: true,
      can_pin_messages: true,
      can_promote_members: false,
      can_manage_chat: true
    });
    bot.sendMessage(chatId, `✅ تم رفع ${msg.reply_to_message.from.first_name} ادمن`);
  }catch(e){
    bot.sendMessage(chatId, 'ما قدرت ارفعه! تأكد البوت مشرف وعنده صلاحية اضافة مشرفين\n' + e.message);
  }
});

// تنزيل ادمن
bot.onText(/^(تنزيل ادمن|تنزيل مشرف)$/, async (msg)=>{
  const chatId = msg.chat.id;
  if(!activeGroups.has(chatId)) return;
  if(!msg.reply_to_message) return bot.sendMessage(chatId, 'رد على رسالة الشخص!');

  try{
    const targetId = msg.reply_to_message.from.id;
    await bot.promoteChatMember(chatId, targetId, {
      can_delete_messages: false,
      can_restrict_members: false,
      can_pin_messages: false,
      can_promote_members: false,
      can_manage_chat: false
    });
    bot.sendMessage(chatId, `✅ تم تنزيل ${msg.reply_to_message.from.first_name} من الادمنية`);
  }catch(e){
    bot.sendMessage(chatId, 'ما قدرت انزله!');
  }
});

bot.onText(/\/start/, (msg)=>{
  bot.sendMessage(msg.chat.id, `هلا ${msg.from.first_name} 👑\nضيفني الجروب وارفعني مشرف واكتب تفعيل`);
});
