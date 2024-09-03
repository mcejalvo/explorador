import discord
import asyncio
import pandas as pd
import threading
import os
from datetime import datetime, timezone
import sys
import argparse
import time

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(os.path.join(parent_dir, 'app'))

from filemanager import open_file, save_file

# Argument parser setup
parser = argparse.ArgumentParser(description="Discord Data Query Script")
parser.add_argument('--reset', action='store_true', help="Reset the data file and query all data")
parser.add_argument('--limit', type=int, help="Limit the total number of messages to fetch (for testing)")
args = parser.parse_args()

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("Discord token not found")

messages = []
DATA_FILE_ID = "11XAt4ezwKcflgqTCCmSDPTDtR29kNGkK"
USERS_DATA_FILE_ID = "1zZQMcdUMkiBdHkmChXq8YD4hQFEglT8w"
LOG_FILE_ID = "1MigJVfJxzoOKpMrKURhmLL64stVRB_Rq"

# Load the user list from Google Drive
user_list = list(open_file(USERS_DATA_FILE_ID)["user"])

# Initialize `existing_data` to ensure it's always defined
existing_data = pd.DataFrame(columns=["name", "message", "timestamp", "channel_name", "thread_name", "message_link", "has_image", "image_url", "total_reactions", "max_reaction_count"])

# Handle the reset argument with confirmation
if args.reset:
    confirmation = input("Are you sure you want to reset the data file? This action cannot be undone. Type 'yes' to proceed: ")
    if confirmation.lower() == 'yes':
        print("Resetting the data file...")
        # Create a new empty DataFrame with the header only
        save_file(existing_data, DATA_FILE_ID)
        start_date = None  # Query all messages since we reset the data
    else:
        print("Reset operation canceled. Exiting...")
        sys.exit(0)
else:
    # Try to load the existing data from Google Drive
    try:
        existing_data = open_file(DATA_FILE_ID)
        if existing_data.empty:
            print("Existing data file is empty. Creating a new DataFrame.")
            start_date = None  # Query all messages if the data is empty
        else:
            existing_data['timestamp'] = pd.to_datetime(existing_data['timestamp'], format='ISO8601', errors='coerce')
            existing_data = existing_data.dropna(subset=['timestamp'])
            last_message_time = existing_data['timestamp'].max()
            start_date = last_message_time
    except Exception as e:
        print(f"Error loading existing data: {str(e)}. Creating a new DataFrame.")
        start_date = None  # Query all messages if there was an error loading the data

class MyBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs, intents=intents)

    async def on_ready(self):
        print(f'Logged in as {self.user}')
        await self.extract_messages_from_all_guilds()
        await self.close()

    async def extract_messages_from_all_guilds(self):
        print("Bot is ready and will now try to fetch messages from all channels and threads in all guilds.")
        
        total_messages_fetched = 0
        
        for guild in self.guilds:
            print(f"Fetching messages from guild: {guild.name}")
            
            for channel in guild.text_channels:
                print(f"Fetching messages from channel: {channel.name}")
                
                try:
                    async for message in channel.history(limit=None, after=start_date):
                        if message.author.name in user_list:
                            has_image = "no"
                            image_url = None
                            if message.attachments:
                                has_image = "yes"
                                image_url = ", ".join([attachment.url for attachment in message.attachments])
                            
                            total_reactions = sum(reaction.count for reaction in message.reactions)
                            max_reaction_count = max((reaction.count for reaction in message.reactions), default=0)
                            message_link = f"https://discord.com/channels/{guild.id}/{channel.id}/{message.id}"
                            messages.append([message.author.name, message.content, message.created_at, channel.name, None, message_link, has_image, image_url, total_reactions, max_reaction_count])
                            
                            total_messages_fetched += 1
                            if args.limit and total_messages_fetched >= args.limit:
                                print(f"Reached total message limit of {args.limit}. Stopping...")
                                return
                    
                    for thread in channel.threads:
                        print(f"Fetching messages from thread: {thread.name}")
                        async for message in thread.history(limit=None, after=start_date):
                            if message.author.name in user_list:
                                has_image = "no"
                                image_url = None
                                if message.attachments:
                                    has_image = "yes"
                                    image_url = ", ".join([attachment.url for attachment in message.attachments])
                                
                                total_reactions = sum(reaction.count for reaction in message.reactions)
                                max_reaction_count = max((reaction.count for reaction in message.reactions), default=0)
                                message_link = f"https://discord.com/channels/{guild.id}/{thread.id}/{message.id}"
                                messages.append([message.author.name, message.content, message.created_at, channel.name, thread.name, message_link, has_image, image_url, total_reactions, max_reaction_count])
                                
                                total_messages_fetched += 1
                                if args.limit and total_messages_fetched >= args.limit:
                                    print(f"Reached total message limit of {args.limit}. Stopping...")
                                    return
                
                except Exception as e:
                    print(f"Could not fetch messages from {channel.name}: {str(e)}")

    async def close(self):
        await super().close()
        print("Bot has been closed.")

def get_discord_data():
    def start_bot():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        bot = MyBot()
        loop.run_until_complete(bot.start(TOKEN))

    thread = threading.Thread(target=start_bot)
    thread.start()
    thread.join()

    new_data = pd.DataFrame(messages, columns=["name", "message", "timestamp", "channel_name", "thread_name", "message_link", "has_image", "image_url", "total_reactions", "max_reaction_count"])
    new_data["date"] = pd.to_datetime(new_data["timestamp"]).dt.date
    new_data["hour"] = pd.to_datetime(new_data["timestamp"]).dt.hour
    new_data['has_spoilers'] = new_data['image_url'].astype(str).str.contains('SPOILER', case=False, na=False).map({True: 'yes', False: 'no'})
    
    return new_data.sort_values(by="timestamp", ascending=False)

def update_log_file(log_file_id, log_data):
    try:
        log_df = open_file(log_file_id)
    except Exception as e:
        print(f"Log file not found or error occurred: {str(e)}. Creating a new log file.")
        log_df = pd.DataFrame(columns=["datetime", "rows_added", "total_rows", "time_spent", "success", "error_message", "limit", "reset"])

    log_df = pd.concat([log_df, pd.DataFrame([log_data])], ignore_index=True)
    save_file(log_df, log_file_id)

def main():
    start_time = time.time()
    try:
        new_data = get_discord_data()
        
        if existing_data.empty:
            updated_data = new_data
        elif new_data.empty:
            updated_data = existing_data
        else:
            updated_data = pd.concat([existing_data, new_data]).drop_duplicates().reset_index(drop=True)

        save_file(updated_data, DATA_FILE_ID)
        
        success = True
        error_message = ""
    except Exception as e:
        success = False
        error_message = str(e)
        print(f"Error during update: {error_message}")
    
    end_time = time.time()
    time_spent = round((end_time - start_time) / 60, 2)  # Convert to minutes
    rows_added = len(new_data) if success else 0
    total_rows = len(updated_data) if success else len(existing_data)
    
    log_entry = {
        "datetime": datetime.now(timezone.utc).isoformat(),
        "rows_added": rows_added,
        "total_rows": total_rows,
        "time_spent": time_spent,  # This is now in minutes
        "success": success,
        "error_message": error_message,
        "limit": args.limit if args.limit else None,
        "reset": args.reset
    }
    
    update_log_file(LOG_FILE_ID, log_entry)

if __name__ == "__main__":
    main()
