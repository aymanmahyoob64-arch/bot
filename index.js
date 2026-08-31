const { Telegraf } = require('telegraf');
const BOT_TOKEN = process.env.BOT_TOKEN;
const bot = new Telegraf(BOT_TOKEN);
bot.start((ctx) => ctx.reply('أهلا يا أيمن! البوت شغال ✅'));
bot.on('text', (ctx) => ctx.reply('وصلتني: ' + ctx.message.text));
bot.launch();
console.log('Bot started');
