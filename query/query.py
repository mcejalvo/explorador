import discord
import asyncio
import pandas as pd
import threading
import os
from datetime import datetime, timezone
import shutil
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(os.path.join(parent_dir, 'app'))

# Now you can import filemanager
from filemanager import *

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("Discord token not found")

messages = []
user_list = list(open_file("query/users.csv")["user"])
DATA_FILE = "data/data.csv"
DATA_FILE_COPY = "data/data-copy.csv"

# Set your start date (only fetch messages after this date)
if os.path.exists(DATA_FILE):
    existing_data = open_file(DATA_FILE)
    # Convert the 'timestamp' column to datetime
    existing_data['timestamp'] = pd.to_datetime(existing_data['timestamp'], format='ISO8601')
    # Find the latest timestamp
    last_message_time = existing_data['timestamp'].max()
else:
    last_message_time = datetime(2021, 1, 1, tzinfo=timezone.utc)

start_date = last_message_time
# start_date = datetime(2024, 8, 20, tzinfo=timezone.utc) # to test

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
                            
                            message_link = f"https://discord.com/channels/{guild.id}/{channel.id}/{message.id}"
                            messages.append([message.author.name, message.content, message.created_at, channel.name, None, message_link, has_image, image_url])
                    
                    for thread in channel.threads:
                        print(f"Fetching messages from thread: {thread.name}")
                        async for message in thread.history(limit=None, after=start_date):
                            if message.author.name in user_list:
                                has_image = "no"
                                image_url = None
                                if message.attachments:
                                    has_image = "yes"
                                    image_url = ", ".join([attachment.url for attachment in message.attachments])

                                message_link = f"https://discord.com/channels/{guild.id}/{thread.id}/{message.id}"
                                messages.append([message.author.name, message.content, message.created_at, channel.name, thread.name, message_link, has_image, image_url])
                
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

    new_data = pd.DataFrame(messages, columns=["name", "message", "timestamp", "channel_name", "thread_name", "message_link", "has_image", "image_url"])
    new_data["date"] = pd.to_datetime(new_data["timestamp"]).dt.date
    new_data["hour"] = pd.to_datetime(new_data["timestamp"]).dt.hour
    
    return new_data.sort_values(by="timestamp", ascending=False)

# Backup the existing data.csv to data-copy.csv
if os.path.exists(DATA_FILE):
    shutil.copyfile(DATA_FILE, DATA_FILE_COPY)

new_data = get_discord_data()

# Append new data to the existing CSV
if os.path.exists(DATA_FILE):
    append_to_encrypted_file(new_data, DATA_FILE)
else:
    save_file(new_data, DATA_FILE)