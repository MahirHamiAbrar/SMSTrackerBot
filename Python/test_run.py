import json
import SMSInfoParser
import TelegramBot

############# ADD THESE ####################
# SMS Info Parser Object
parser = SMSInfoParser.SMSInfoParser()
# telegram-MessageTrackerBot object
telegramBot = TelegramBot.MessageTrackerBot(TelegramBot.BOT_TOKEN)
message_store = telegramBot.start()
###########################################

def getDonatorName(username: str) -> str | None:
    USERLIST_FILENAME = "username-list.json"
    
    data = None
    
    try:
        with open(USERLIST_FILENAME, 'r') as file:
            data = json.loads(file)
        
        if username not in data:
            return None
    
    except Exception as e:
        print(f"Error: {e}")
        return None
    
    return data[username]

def processSMS():
    data = message_store.get()    # the sms string from user input field
    
    if data is None:
        return
    
    try:
        sms = data['text']
        username = data['username']   # get username from login cache
        
        if username is None:
            telegramBot.sendReply(data['message-obj'], "DECLINED.\nYou are an UNREGISTERED USER!")
            return
        
        result = parser.parseSMS(sms)
        
        # check for blank returns
        if result in [None, {}]:
            # the data parsing was not successful. Show an error message.
            print("the data parsing was not successful")
            telegramBot.sendReply(data['message-obj'], "Invalid SMS. Please Send Again.")
            return # do not proceed
        
        # else: do stuff here
        
        timestamp = result['timestamp']
        trxid = result['trxid']
        amount = result['amount']
        last_4_digits = result['last-4-digits']
        
        array = [timestamp, last_4_digits, trxid, amount, username]
        
        reply_data = f"Username: {username}\n" \
                     f"Amount: {amount}\n" \
                     f"TrxID: {trxid}\n" \
                     f"Last 4 Digits: {last_4_digits}\n" \
                     f"timestamp: {timestamp}\n"

        telegramBot.sendReply(data['message-obj'], f"PROCESSED.\n\n{reply_data}")
        
        print(array)
    except Exception as e:
        telegramBot.sendReply(data['message-obj'], f"Invalid Data!\nError Details: {e}")
        return


if __name__ == '__main__':
    
    while True:
        processSMS()
