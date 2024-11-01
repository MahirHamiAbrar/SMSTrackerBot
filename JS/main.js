import { SMSInfoParser } from "./SMSInfoPerser.js";
import { addRowToGoogleSheet } from "./GoogleSheets.js";
import { launch_telegram_bot, getUserFullName } from "./TelegramBot.js";

// an LLM based info parser object
const parser = new SMSInfoParser();

// handle special cases when the transaction-id (trxid) can be NULL
// and the phone number might become something NOT-A-PHONENUMBER!
function handleSpecialCases(sms, trxid, phone) {
    if (sms.includes("Rupali Bank")) {
        trxid = "N/A";
        phone = "Rupali Bank";
    }
    else if (sms.includes("***") && sms.includes("NexusPay")) {
        trxid = "N/A";
        phone = "DBBL";
    }

    return [trxid, phone];
}

// the main function that will be responsible for 
// receiving messages, processing them and then replying to them.
async function botWorkerFunction(context) {

    try {
        const sms = context.message.text;

        // get JSON response from LLM
        var result = await parser.parseContent(sms);

        // extract info from the result
        const timestamp = result['timestamp'];
        const amount = result['received-amount'];
        const phonenumber = result['sender'];
        // collect username from telegram bot
        const username = getUserFullName(context.message.from);
        const isdigit = result['sender-has-number'];

        console.log("Received AI Response: ", result);
        
        // create mutable variables for transaction ID and phonenumber
        // as they might change later on.
        var trxid = result['trxid'];
        var reply_text = "";

        // check if all necessary data are present or not
        if (!timestamp || !amount || !phonenumber || !trxid) {
            reply_text = "Insufficient Data Provided. Please RESEND.";
            console.log(reply_text);
        } else {
            var last_4_digits = phonenumber.slice(phonenumber.length - 4, phonenumber.length);

            // handle special cases for traxid and last-4-digits of the phonenumber
            [trxid, last_4_digits] = handleSpecialCases(sms, trxid, last_4_digits);

            if (!isdigit) {
                last_4_digits = phonenumber;
            }

            // create a reply message
            reply_text = `Username: ${username}\n` +
                         `Amount: ${amount}\n` +
                         `TrxID: ${trxid}\n` +
                         `Last 4 Digits: ${last_4_digits}\n` +
                         `timestamp: ${timestamp}\n`;
            
            // append a row to the google sheet
            await addRowToGoogleSheet([timestamp, "", last_4_digits, trxid, amount, username]);
        }

        // reply to the message bot just processed (using context shortcut)
        await context.reply(reply_text, {
                reply_to_message_id: context.message.message_id
            }
        );
    } catch (err) {
        console.log("Error Occured in botWorkerFunction:", err);

        await context.reply("Server Error. Please try again shortly.", {
            reply_to_message_id: context.message.message_id
        });
    }
}

// launch the telegram bot and run indefinitely
await launch_telegram_bot(botWorkerFunction);

`
You have received deposit from iBanking of Tk 5,000.00 from BRAC Bank Internet Banking. Fee Tk 0.00. Balance Tk 31,958.37. TrxID BK16VEMBXA at 01/11/2024 16:52
`