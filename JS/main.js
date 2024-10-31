import { SMSInfoParser } from "./SMSInfoPerser.js";
import { addRowToGoogleSheet } from "./GoogleSheets.js";
import { launch_telegram_bot, getUserFullName } from "./TelegramBot.js";

// an LLM based info parser object
const parser = new SMSInfoParser();

// the main function that will be responsible for 
// receiving messages, processing them and then replying to them.
async function botWorkerFunction(context) {
    // get JSON response from LLM
    var result = await parser.parseContent(context.message.text);

    // extract info from the result
    const timestamp = result['timestamp'];
    const trxid = result['trxid'];
    const amount = result['received-tk'];
    const last_4_digits = result['phonenumber'];
    const username = getUserFullName(context.message.from);   // get username from login cache

    // create a reply message
    const reply_text = `Username: ${username}\n` +
                       `Amount: ${amount}\n` +
                       `TrxID: ${trxid}\n` +
                       `Last 4 Digits: ${last_4_digits}\n` +
                       `timestamp: ${timestamp}\n`;
    
    // append a row to the google sheet
    addRowToGoogleSheet([timestamp, "", last_4_digits, trxid, amount, username]);

    // reply to the message bot just processed (using context shortcut)
    await context.reply(reply_text, {
            reply_to_message_id: context.message.message_id
        }
    );
}

// launch the telegram bot and run indefinitely
await launch_telegram_bot(botWorkerFunction);
