import SMSInfoParser from './SMSInfoParser.js';

const parser = new SMSInfoParser();

const smsString = "Dear Sir, your A/C ***2385 credited (Fund Transfer) by Tk2347.00 on 01-04-2026 11:15:07 AM C/B Tk5000.00. NexusPay https://bit.ly/nexuspay"
const result = await parser.parseSMS(smsString);
console.log(result);

// async function main() {
//     const TEST_SMS = `
//         Money Received.
//         Amount: Tk 200.00
//         Sender: 12342384738
//         Ref: donation for human
//         TxnID: 77SDBKWM23UOR
//         Balance: Tk 205.22
//         29/10/2024 12:03
//     `;

//     try {
//         const parser = new SMSInfoParser();
//         await parser.initializeParser(); // Wait for initialization to complete
//         console.log('working...');
//         const result = await parser.parseSMS(TEST_SMS.trim());
//         console.log(JSON.stringify(result, null, 4));
//     } catch (error) {
//         console.error(`Error in main: ${error}`);
//     }
// }

// while (true) {main();}
