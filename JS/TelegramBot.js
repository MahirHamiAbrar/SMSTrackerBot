import { Telegraf } from "telegraf";
import { message } from "telegraf/filters";
import { createRequire } from "node:module";

// make use of 'require' in ES modules
const require = createRequire(import.meta.url);
const _telegram_bot_token = require("../ai-bot-credentials.json");

const bot = new Telegraf(
    _telegram_bot_token["telegram-bot-testing-service-access-token"]
);

function getUserFullName(user) {
    var name = user.first_name;

    if (user.last_name) {
        name += ` ${user.last_name}`;
    }

    return name;
}

bot.on(message('text'), async (context) => {    
    // using context shortcut
    await context.reply(`Hellow, ${getUserFullName(context.message.from)}`, {
            reply_to_message_id: context.message.message_id
        }
    );
});

bot.launch();

process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
