// import groq SDK
import Groq from "groq-sdk";
// import the system prompt
import { GROQ_SYSTEM_PROMPT_CONTENT } from "./prompts.js";
import { CONFIG_CREDENTIALS as credentialData } from "./utils.js";


export class SMSInfoParser {

  constructor() {
    // some AI models according to the developer's preference!
    this._AVAILABLE_MODELS = [
      "llama-3.2-90b-text-preview",
      "llama-3.2-11b-text-preview",
      "llama3-8b-8192",
      "llama3-70b-8192",
      "mixtral-8x7b-32768"
    ];
    
    // the LLM in use
    this.groq_model_name = this._AVAILABLE_MODELS[0];

    // Groq object
    this.groq = new Groq({
      apiKey: credentialData["groq-api-key"]
    });
  }

  async getGroqChatCompletion(input_query) {
    // get chat completion first
    var chat_completion = await this.groq.chat.completions.create({
      messages: [
        {
            "role": "system",
            "content": GROQ_SYSTEM_PROMPT_CONTENT
        },
        {
            "role": "user",
            "content": input_query,
        }
      ],
      model: this.groq_model_name,
    });

    // return either an empty string or LLM response text
    return (chat_completion.choices[0]?.message?.content || "");
  }

  async parseContent(sms) {
    // get AI completion text
    var jsonResponse = await this.getGroqChatCompletion(sms);

    // check for blank text
    if (jsonResponse == "") {
      return "";
    }

    // load as a JSON object
    jsonResponse = JSON.parse(jsonResponse);
    // console.log(jsonResponse);  // print

    return jsonResponse;
  }
}


export async function main() {
  const parser = new SMSInfoParser();

  const sms = `
        Money Received.
        Amount: Tk 200.00
        Sender: 12342384738
        Ref: donation for human
        TxnID: 77SDBKWM23UOR
        Balance: Tk 205.22
        29/10/2024 12:03
  `;
  const data = await parser.parseContent(sms);
  console.log(data);
}

// await main();
