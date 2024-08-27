import discord
import asyncio
import pandas as pd
import threading

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("Discord token not found")

messages = []
# List of users to filter
user_list = pd.read_csv("query/users.csv")

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
                    async for message in channel.history(limit=None):
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
                        async for message in thread.history(limit=None):
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

    df = pd.DataFrame(messages, columns=["name", "message", "timestamp", "channel_name", "thread_name", "message_link", "has_image", "image_url"])
    df["date"] = pd.to_datetime(df["timestamp"]).dt.date
    df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour
    
    return df

# Example usage
df = get_discord_data()

df.to_csv("data/data1.csv", index=False, quoting=0)
