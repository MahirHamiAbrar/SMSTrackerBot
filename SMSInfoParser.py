"""This is an information parser for the transaction messages comming from Bkash, Nagad, Rocket and
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
from prompt import __GROQ_SYSTEM_PROMPT


# GROQ System Prompt
GROQ_SYSTEM_PROMPT_CONTENT = __GROQ_SYSTEM_PROMPT


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
        
        # handle 'DBBL' special case
        # if any([elem in sms for elem in ['NexusPay', 'Rupali Bank']]):

        if 'NexusPay' in sms:
            ai_resp['trxid'] = 'N/A'
            ai_resp['phonenumber'] = "DBBL"

        elif 'Rupali Bank' in sms:
            ai_resp['trxid'] = 'N/A'
            ai_resp['phonenumber'] = "Rupali Bank"

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
    
    TEST_SMS = """
        Rupali Bank PLC.

        Dear Sir,
        Your A/C:4570**1296
        CREDITED(Transfer) by TK.
        123894.00 ON 13-12-2011 from
        RUET Br.RAJ..
        BAL:TK.5392
        Thank You.
    """
    
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
