import os
import json
import telebot
import threading
from typing import Any
from datetime import datetime
from collections import deque
from queue import Queue, Empty

class MessageStore:
    def __init__(self):
        """Store for keeping track of messages using a thread-safe deque."""
        self.messages = deque()  # Unlimited message storage
        self.lock = threading.Lock()
        self.new_message_event = threading.Event()  # For signaling new messages
    
    def add_message(self, username, text, timestamp, message_obj):
        """Add a message to the store."""
        with self.lock:
            self.messages.append({
                'username': username,
                'text': text,
                'timestamp': timestamp,
                'message-obj': message_obj
            })
            self.new_message_event.set()  # Signal that a new message is available
    
    def get_messages(self, start_idx=0, count=50):
        """
        Return a slice of messages with pagination support.
        start_idx: starting index for pagination
        count: number of messages to return
        """
        with self.lock:
            messages_list = list(self.messages)
            end_idx = min(start_idx + count, len(messages_list))
            return messages_list[start_idx:end_idx]
    
    def get_total_count(self):
        """Return total number of messages stored."""
        with self.lock:
            return len(self.messages)
    
    def get(self) -> Any | None:
        if len(self.messages) == 0:
            return None
        return self.messages.popleft()
            

class MessageTrackerBot:
    def __init__(self, token):
        """Initialize bot with API token."""
        self.bot = telebot.TeleBot(token)
        self.message_queue = Queue()  # Queue for incoming messages
        self.is_running = True
        self.message_store = MessageStore()

        # Register message handler
        @self.bot.message_handler(func=lambda message: True)
        def echo_all(message):
            self.message_queue.put(message)
        
        # self.bot.add_message_handler(telebot.CommandHandler('start', self.start_cmd_handler))
        
        @self.bot.message_handler(commands=['register'])
        def sifat_command(message):
            """ Handle the /sifat command with subcommands """
            args = message.text.split()[1:]
            if len(args) > 0:
                subcommand = args[0].lower()
                print(subcommand)

    def process_messages(self):
        """Process messages from queue in a separate thread."""
        while self.is_running:
            try:
                # Get message from queue with timeout
                try:
                    message = self.message_queue.get(timeout=1.0)
                except Empty:
                    continue

                # Process the message
                # username = message.from_user
                # print(dir(message.from_user))
                username = message.from_user.full_name
                # username = message.from_user.username or f"User{message.from_user.id}"
                timestamp = datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
                
                # Store the message
                self.message_store.add_message(username, message.text, timestamp, message)
                
                # Echo back to Telegram
                # self.bot.reply_to(message, "Processed.")
                
                # Mark the task as done
                self.message_queue.task_done()
                
            except Exception as e:
                print(f"Error processing message: {e}")
    
    def sendReply(self, message_obj, reply_text: str = "Processed.") -> None:
        self.bot.reply_to(message_obj, reply_text)

    def start(self):
        """Start the bot in separate threads."""
        # Start message processing thread
        processor_thread = threading.Thread(target=self.process_messages)
        processor_thread.daemon = True
        processor_thread.start()
        
        # Start polling thread
        polling_thread = threading.Thread(target=self._polling)
        polling_thread.daemon = True
        polling_thread.start()

        print("Bot started with unlimited message storage.")
        return self.message_store  # Return message store for Flask app to use

    def _polling(self):
        """Polling method to run in separate thread."""
        print("Bot started polling.")
        self.bot.polling(none_stop=True)

    def stop(self):
        """Stop the bot and message processing."""
        self.is_running = False
        self.bot.stop_polling()
        # Wait for remaining messages to be processed
        self.message_queue.join()
        print("Bot stopped gracefully.")

def readToken():
    CREDENTIALS_FILE = "ai-bot-credentials.json"
    if not os.path.exists(CREDENTIALS_FILE):
        return None
    
    data = None
    
    try:
        with open(CREDENTIALS_FILE, 'r') as file:
            data = json.load(file)
        data = data["telegram-bot-access-token"]
        
    except Exception as e:
        print(f"Error Occured While Reading BOT TOKEN: {e}")
        return None
    
    return data

# Initialize bot with token
BOT_TOKEN = readToken()

if not BOT_TOKEN:
    print("ERROR READING TELEGRAM-BOT TOKEN. ABORTING.")
    exit(-1)

