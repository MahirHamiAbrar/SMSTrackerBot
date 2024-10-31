import SMSInfoParser
import TelegramBot
# from flask import Flask, request, jsonify, render_template
from google.oauth2 import service_account
from googleapiclient.discovery import build

############# ADD THESE ####################
# SMS Info Parser Object
parser = SMSInfoParser.SMSInfoParser()
# telegram-MessageTrackerBot object
telegramBot = TelegramBot.MessageTrackerBot(TelegramBot.BOT_TOKEN)
message_store = telegramBot.start()
###########################################


# Set up Google Sheets API credentials
# SERVICE_ACCOUNT_FILE = '/home/updateSheetTelebot/credentials.json'
SERVICE_ACCOUNT_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=credentials)

# Your Google Sheet ID and the range you want to work with
SPREADSHEET_ID = '10h9WEo_-mEJz-ICPh-aIvN3_tAHwmna11U4hC7AcYz4'
SHEET_RANGE = 'List of Donor!A:G'  # Adjust the range as needed and sheet Name

def processSMS():
    data = message_store.get()    # the sms string from user input field

    if data is None:
        return

    try:
        sms = data['text']
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
        username = data['username']   # get username from login cache

        array = [timestamp,"" ,last_4_digits, trxid, amount,username ]

        reply_data = f"Username: {username}\n" \
                     f"Amount: {amount}\n" \
                     f"TrxID: {trxid}\n" \
                     f"Last 4 Digits: {last_4_digits}\n" \
                     f"timestamp: {timestamp}\n"

        telegramBot.sendReply(data['message-obj'], f"PROCESSED.\n\n{reply_data}")

         # Append data to the Google Sheet
        sheet = service.spreadsheets()
        result = sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=SHEET_RANGE,
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": [array]}
        ).execute()

        print(array)
    except Exception as e:
        telegramBot.sendReply(data['message-obj'], f"Invalid Data!\nError Details: {e}")
        return


if __name__ == '__main__':
    while True:
        try:
            processSMS()
        except Exception as e:
            print(f"Error: {e}")
