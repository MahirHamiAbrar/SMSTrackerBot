import { Telegraf } from "telegraf";
import { message } from "telegraf/filters";
import { CONFIG_CREDENTIALS as _telegram_bot_token, choose_tp } from "./utils.js";

const bot = new Telegraf(
    _telegram_bot_token[choose_tp(
        "telegram-bot-testing-service-access-token",
        "telegram-bot-access-token"
    )]
);

export function getUserFullName(user) {
    var name = user.first_name;

    if (user.last_name) {
        name += ` ${user.last_name}`;
    }

    return name;
}

export async function launch_telegram_bot(work_func) {
    bot.on(message('text'), async (context) => work_func(context));
    bot.launch({
        allowedUpdates: ["message", "message_reaction"]
    });

    process.once('SIGINT', () => bot.stop('SIGINT'));
    process.once('SIGTERM', () => bot.stop('SIGTERM'));
}
