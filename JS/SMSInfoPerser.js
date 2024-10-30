// import groq SDK
import Groq from "groq-sdk";
// import createRequire to use 'require' in ES modules!
import { createRequire } from "node:module";

// create require method
const require = createRequire(import.meta.url);

// now import the JSON credentials file
const credentialData = require("../ai-bot-credentials.json");

console.log(credentialData["groq-api-key"]);
exit(0);

const groq = new Groq({
    apiKey: "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"
});


export async function main() {
    const chatCompletion = await getGroqChatCompletion();
    var completion = chatCompletion.choices[0]?.message?.content;
    console.log(completion || "");
}

export async function getGroqChatCompletion() {
    return groq.chat.completions.create({
        messages: [
          {
            role: "user",
            content: "Explain the importance of fast language models",
          },
        ],
        model: "llama3-8b-8192",    
    });
}

main();

