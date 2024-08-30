import discord
import asyncio
import pandas as pd
import threading
import os
from datetime import datetime, timezone
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(os.path.join(parent_dir, 'app'))

# Now you can import filemanager
from filemanager import open_file, save_file

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("Discord token not found")

messages = []
DATA_FILE_ID = "1OkrKe5jT3fwq4B3Z_VMOm9WpHysjvAQ5"
USERS_DATA_FILE_ID = "1zZQMcdUMkiBdHkmChXq8YD4hQFEglT8w"

# Load the user list from Google Drive
user_list = list(open_file(USERS_DATA_FILE_ID)["user"])

# Try to load the existing data from Google Drive
try:
    existing_data = open_file(DATA_FILE_ID)
    if existing_data.empty:
        print("Existing data file is empty. Creating a new DataFrame.")
        # Create an empty DataFrame with the desired structure if the file is empty
        existing_data = pd.DataFrame(columns=["name", "message", "timestamp", "channel_name", "thread_name", "message_link", "has_image", "image_url", "total_reactions"])
        start_date = None  # Query all messages if the data is empty
    else:
        existing_data['timestamp'] = pd.to_datetime(existing_data['timestamp'], format='ISO8601', errors='coerce')
        # Filter out rows where 'timestamp' is NaT
        existing_data = existing_data.dropna(subset=['timestamp'])
        last_message_time = existing_data['timestamp'].max()
        start_date = last_message_time
except Exception:
    print("Error loading existing data. Creating a new DataFrame.")
    start_date = None  # Query all messages if there was an error loading the data
    existing_data = pd.DataFrame(columns=["name", "message", "timestamp", "channel_name", "thread_name", "message_link", "has_image", "image_url", "total_reactions"])

class MyBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs, intents=intents)

    async def on_ready(self):
        print(f'Logged in as {self.user}')
        await self.extract_messages_from_all_guilds()
        await self.close()  # Close the bot after fetching the messages

    async def extract_messages_from_all_guilds(self):
        print("Bot is ready and will now try to fetch messages from all channels and threads in all guilds.")
        
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
                            
                            # Sum the total reactions for this message
                            total_reactions = sum(reaction.count for reaction in message.reactions)
                            
                            message_link = f"https://discord.com/channels/{guild.id}/{channel.id}/{message.id}"
                            messages.append([message.author.name, message.content, message.created_at, channel.name, None, message_link, has_image, image_url, total_reactions])
                    
                    for thread in channel.threads:
                        print(f"Fetching messages from thread: {thread.name}")
                        async for message in thread.history(limit=None, after=start_date):
                            if message.author.name in user_list:
                                has_image = "no"
                                image_url = None
                                if message.attachments:
                                    has_image = "yes"
                                    image_url = ", ".join([attachment.url for attachment in message.attachments])
                                
                                # Sum the total reactions for this message
                                total_reactions = sum(reaction.count for reaction in message.reactions)
                                
                                message_link = f"https://discord.com/channels/{guild.id}/{thread.id}/{message.id}"
                                messages.append([message.author.name, message.content, message.created_at, channel.name, thread.name, message_link, has_image, image_url, total_reactions])
                
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
    thread.join()  # Wait for the thread to finish

    new_data = pd.DataFrame(messages, columns=["name", "message", "timestamp", "channel_name", "thread_name", "message_link", "has_image", "image_url", "total_reactions"])
    new_data["date"] = pd.to_datetime(new_data["timestamp"]).dt.date
    new_data["hour"] = pd.to_datetime(new_data["timestamp"]).dt.hour
    
    # Add 'has_spoilers' column based on 'image_url' containing 'SPOILER'
    new_data['has_spoilers'] = new_data['image_url'].astype(str).str.contains('SPOILER', case=False, na=False).map({True: 'yes', False: 'no'})
    
    return new_data.sort_values(by="timestamp", ascending=False)

new_data = get_discord_data()

# Append new data to the existing DataFrame and save back to Google Drive
updated_data = pd.concat([existing_data, new_data]).drop_duplicates().reset_index(drop=True)
save_file(updated_data, DATA_FILE_ID)
