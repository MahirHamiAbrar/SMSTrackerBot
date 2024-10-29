// This is an information parser for transaction messages from Bkash, Nagad, Rocket and
// similar services, powered by LLMs.

import fs from 'fs/promises';
import path from 'path';

const GROQ_SYSTEM_PROMPT_CONTENT = `You are a very helpful assistant who responds with only JSON data. The user will provide you with an SMS message related with notification about money transferring. Your task is to extract these 5 info from the message and create a JSON dictionary with that.
DO NOT MODIFY THE EXTRACTED INFORMATION, KEEP THEM AS IS, BECAUSE THEY ARE SUPER IMPORTANT CREDENTIALS.

The fields are:
    - timestamp
    - phonenumber
    - trxid
    - received-tk

The key of JSON objects MUST follow the same names mentioned in the list above. And you MUST ONLY OUTPUT A SINGLE JSON OBJECT AND NOTHING ELSE, NO EXTRA TEXT.
If no message provided return only ONE empty json object.

Demo Query and Demo Response:

Demo-Query #1:
Tk55.00 received from A/C:7136423746 Fee:Tk0, Your A/C Balance: Tk286.00 TxnId:7823478376 Date:20-AUG-23 07:48:09 pm. Download https://bit.ly/nexuspay
Demo-Response #1:
{
    "timestamp" : "20-AUG-23 07:48:09 pm",
    "phonenumber" : "7136423746",
    "trxid" : "7823478376",
    "received-tk" : "55.00"
}

Demo-Query #2:
Dear Sir, your A/C ***5678 credited (Fund Transfer) by Tk500.00 on 01-09-2024 02:11:54 AM C/B Tk500.00. NexusPay https://bit.ly/nexuspay
Demo-Response #2:
{
    "timestamp" : "01-09-2024 02:11:54 AM",
    "phonenumber" : "***5678",
    "trxid" : "NexusPay",
    "received-tk" : "500.00"
}

Demo-Query #3:
You have received Tk 100.00 from 01320530845. Ref Rzs. Fee Tk 0.00. Balance Tk 7,773.00. TrxID CJNDFH7348C74 at 29/01/2024 17:13
Demo-Response #3:
{
    "timestamp" : "29/01/2024 17:13",
    "phonenumber" : "01320530845",
    "trxid" : "CJNDFH7348C74",
    "received-tk" : "100.00"
}

Demo-Query #4:
Rupali Bank PLC.

Dear Sir,
Your A/C:3773**0974
CREDITED(Transfer) by TK.
2,250.00 ON 23-06-2024 from
RUET Br.RAJ..
BAL:TK.5392
Thank You.
Demo-Response #4:
{
    "timestamp" : "23-06-2024",
    "phonenumber" : "4570**1296",
    "trxid" : "Rupali Bank PLC.",
    "received-tk" : "2,250.00"
}

Your Response should be similar to the demonstrated Demo-Response sections. I just showed you 4 dummy cases. And the provided Queries will be similar to one of these mentioned above.`;

class SMSInfoParser {
    // Available AI models according to the developer's preference
    static _AVAILABLE_MODELS = [
        "llama-3.2-90b-text-preview",
        "llama-3.2-11b-text-preview",
        "llama3-8b-8192",
        "llama3-70b-8192",
        "mixtral-8x7b-32768"
    ];

    static CREDENTIALS_FILE = "ai-bot-credentials.json";

    constructor() {
        // Initialize the parser
        this.GROQ_MODEL_NAME = SMSInfoParser._AVAILABLE_MODELS[0];
        this.GROQ_API_KEY = null;
        this.client = null;
        
        // Read API key and initialize client
        this.initializeParser();
    }

    async initializeParser() {
        this.GROQ_API_KEY = await this.readAPIKey();
        
        if (!this.GROQ_API_KEY) {
            console.error("Error with API Key reading. Exiting the program.");
            throw new Error("Failed to initialize parser: Invalid API key");
        }

        // Initialize Groq client
        this.client = {
            api_key: this.GROQ_API_KEY
        };
    }

    async readAPIKey() {
        try {
            // Read the local JSON file using fs.promises
            const filePath = path.join(process.cwd(), SMSInfoParser.CREDENTIALS_FILE);
            const fileContent = await fs.readFile(filePath, 'utf8');
            const data = JSON.parse(fileContent);
            return data["groq-api-key"];
        } catch (error) {
            console.error(`Error occurred while reading API Key: ${error}`);
            return null;
        }
    }

    async _get_ai_response(sms) {
        try {
            const response = await fetch('https://api.groq.com/v1/chat/completions', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.GROQ_API_KEY}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    messages: [
                        {
                            role: "system",
                            content: GROQ_SYSTEM_PROMPT_CONTENT
                        },
                        {
                            role: "user",
                            content: String(sms)
                        }
                    ],
                    model: this.GROQ_MODEL_NAME
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return JSON.parse(data.choices[0].message.content);
        } catch (error) {
            console.error(`Exception Occurred: ${error}`);
            return null;
        }
    }

    async parseSMS(sms) {
        try {
            const ai_resp = await this._get_ai_response(sms);
            console.log("AI-Resp: " + ai_resp);
            
            if (!ai_resp) {
                console.error("Error! Aborting!");
                return {};
            }

            let last_4_digits = ai_resp['phonenumber'];
            
            if ([..."0123456789"].some(num => last_4_digits.includes(num)) && 
                !last_4_digits.includes("*")) {
                const phonenumber_length = last_4_digits.length;
                last_4_digits = String(last_4_digits.slice(phonenumber_length - 4));
            }

            return {
                'timestamp': ai_resp['timestamp'],
                'trxid': ai_resp['trxid'],
                'amount': String(ai_resp['received-tk']),
                'last-4-digits': last_4_digits,
                'phonenumber': String(ai_resp['phonenumber'])
            };
        } catch (error) {
            console.error(`Error parsing SMS: ${error}`);
            return {};
        }
    }
}

// Example usage
async function main() {
    const TEST_SMS = `
        Money Received.
        Amount: Tk 200.00
        Sender: 12342384738
        Ref: donation for human
        TxnID: 77SDBKWM23UOR
        Balance: Tk 205.22
        29/10/2024 12:03
    `;

    try {
        const parser = new SMSInfoParser();
        await parser.initializeParser(); // Wait for initialization to complete
        const result = await parser.parseSMS(TEST_SMS.trim());
        console.log(JSON.stringify(result, null, 4));
    } catch (error) {
        console.error(`Error in main: ${error}`);
    }
}

// Export the class for module usage
export default SMSInfoParser;