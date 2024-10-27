"""This is an information parser from the transaction messages comming from Bkash, Nagad, Rocket and
services like these, powered by LLMs. Of Course I didn't choose LLMs over RegEx because I suck at coding
and don't have enough skill and patience to apply RegEx! Why would you think that? :)

DOCUMENTATION
   - by a human!

usage:
    parser = SMSInfoParser()
    result = parser.parseSMS("sms_string")
    
    # do stuff with 'result' here...
    
the result variable wil contain a JSON object, having the below keys:
    - timestamp
    - trxid
    - amount
    - last-4-digits
    - phonenumber

so for example if you want to access the amount received you can just do:
    amount_tk = result["amount"]

NOTE:   IF THERE IS ANY ERROR, parseSMS() function will return an empty dictionary like this: {}
        MAKE SURE TO CHECK IT BEFORE DOING ANYTHING WITH THE RETURNED-RESULT!

This is that easy!
Enjoy!
"""

# pip install groq
import os
import json
from groq import Groq


# GROQ System Prompt
GROQ_SYSTEM_PROMPT_CONTENT = """You are a very helpful assistant who responds with only JSON data. The user will provide you with an SMS message related with notification about money transferring. Your task is to extract these 5 info from the message and create a JSON dictionary with that.
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

Your Response should be similar to the demonstrated Demo-Response sections. I just showed you 4 dummy cases. And the provided Queries will be similar to one of these mentioned above.
"""


class SMSInfoParser:
    
    # some AI models according to the developer's preference!
    _AVAILABLE_MODELS = [
        "llama-3.2-90b-text-preview",
        "llama-3.2-11b-text-preview",
        "llama3-8b-8192",
        "llama3-70b-8192",
        "mixtral-8x7b-32768"
    ]
    
    CREDENTIALS_FILE = "ai-bot-credentials.json"
    
    def __init__(self) -> None:
        # read the API key
        self.GROQ_API_KEY = self.readAPIKey()
        
        # the AI model that we're going to use
        self.GROQ_MODEL_NAME = self._AVAILABLE_MODELS[0]
        
        # read API key
        if not self.GROQ_API_KEY:
            print("Error with API Key reading. Exiting the program.")
            exit(-1)
            
        # groq client object
        self.client = Groq(
            api_key = self.GROQ_API_KEY,
        )

    def readAPIKey(self) -> str | None:
        """
            If returned 'None', then there was a problem reading the API key.
        """
        
        if not os.path.exists(self.CREDENTIALS_FILE):
            return None
        
        data = None
        
        try:
            with open(self.CREDENTIALS_FILE, 'r') as file:
                data = json.load(file)
            data = data["groq-api-key"]
            
        except Exception as e:
            print(f"Error Occured While Reading API Key: {e}")
            return None
        
        return data
    
    def _get_ai_response(self, sms: str) -> dict | None:
        """
            If returned 'None' instead of 'dict', then there was a problem with AI response.
        """
        
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": GROQ_SYSTEM_PROMPT_CONTENT
                },
                {
                    "role": "user",
                    "content": str(sms),
                }
            ],
            model = self.GROQ_MODEL_NAME,
        )

        response = chat_completion.choices[0].message.content
        
        try:
            response = json.loads(response)
        except Exception as e:
            print(f"Exception Occured: {e}.\nResponse Received: {response}\n")
            return None
        
        return response
    
    def parseSMS(self, sms: str) -> dict:
        """
            In case any error, this will return an empty dictionary.
        """
        
        ai_resp = self._get_ai_response(sms)
        
        if ai_resp is None:
            print("Error! Aboarting!")
            return {}
        
        last_4_digits = ai_resp['phonenumber']
        
        # if "*" not in last_4_digits:
        if (
            any([(num in last_4_digits) for num in "0123456789"]) and
            "*" not in last_4_digits
        ):
            phonenumber_length = len(ai_resp['phonenumber'])
            last_4_digits = str(last_4_digits[(phonenumber_length - 4):])
        
        return {
            'timestamp':        ai_resp['timestamp'],
            'trxid':            ai_resp['trxid'],
            'amount':           str(ai_resp['received-tk']),
            'last-4-digits':    last_4_digits,
            'phonenumber':      str(ai_resp['phonenumber'])
        }


if __name__ == '__main__':
    TEST_SMS = """
        Money Received.
        Amount: Tk 200.00
        Sender: 12342384738
        Ref: donation for human
        TxnID: 77SDBKWM23UOR
        Balance: Tk 205.22
        29/10/2024 12:03
    """
    
    # TEST_SMS = """
    # Dear Sir, your A/C ***2385 credited (Fund Transfer) by Tk2347.00 on 01-04-2026 11:15:07 AM C/B Tk5000.00. NexusPay https://bit.ly/nexuspay
    # """
    
    # TEST_SMS = """
    #     Rupali Bank PLC.

    #     Dear Sir,
    #     Your A/C:4570**1296
    #     CREDITED(Transfer) by TK.
    #     123894.00 ON 13-12-2011 from
    #     RUET Br.RAJ..
    #     BAL:TK.5392
    #     Thank You.
    # """
    
    # TEST_SMS = """
    #     Money Received.
    #     Amount: Tk 50.00
    #     Sender: 01763177922
    #     Ref: N/A
    #     TxnID: 73BNYW1C
    #     Balance: Tk 2580.22
    #     27/10/2024 22:08
    # """
    
    parser = SMSInfoParser()
    result = parser.parseSMS(TEST_SMS.strip())
    
    print(json.dumps(
        result, 
        indent = 4
    ))
