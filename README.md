
# 🚀 Discord Search Dashboard 🚀

Welcome to the **ultimate** tool for stalking—err, I mean *searching*—Discord messages! With this setup, you'll be pulling in messages from Discord, storing them safely on Google Drive, and exploring them through a sleek dashboard built with Streamlit. All automated, all cool. 😎

## 🔥 Features

- **Real-Time Message Fetching**: Get the latest messages from your Discord channels and threads—no more FOMO! 🔥
- **Google Drive Integration**: No local files? No problem. Everything is saved directly to Google Drive. 🌍
- **Sleek Dashboard**: Check out your messages in style with a dashboard that's as smooth as butter. 🍰
- **Lightning Fast**: Thanks to caching, you won’t be waiting around for things to load. ⚡️

## 🛠️ Environment Variables

Make sure you’ve got these set:

- `DISCORD_TOKEN`: Your super-secret Discord bot token. 🤖
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to your `credentials.json`. 🔑
- `TAB_TITLE`: (Optional) Spice up your dashboard title with something fancy. ✨

## 🐳 Docker All the Things!

### Compose Like a Rockstar 🎸

Your `docker-compose.yml` might look something like this:

```yaml
version: '3.7'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    secrets:
      - google_credentials
    environment:
      - DISCORD_TOKEN=your-discord-token
      - GOOGLE_APPLICATION_CREDENTIALS=/app/.secrets/credentials.json

secrets:
  google_credentials:
    file: ./secrets/google_credentials.json
```

## 📜 Scripts Breakdown

### 🖥️ Streamlit Dashboard (`app.py`)

This is your command center where all the magic happens. Launch it, explore it, love it.

**Cool Stuff**:
- Caches data for lightning-fast loading ⚡
- Hit the "Actualizar" button to keep things fresh 🧼

### 🤖 Discord Message Fetcher (`query.py`)

This bot’s on a mission to fetch all the messages from Discord that matter to you.

**Key Features**:
- Fetches messages from everywhere you care about 📥
- Filters them down to the users you want to stalk—er, track 👀
- Saves everything to Google Drive, no mess, no fuss 💾

**New Parameters**:

- `--limit`: Limit the number of messages to fetch (useful for testing). For example, `--limit 100` will fetch only 100 messages. If this parameter is not used, the script will fetch all available messages.
  
- `--reset`: Resets the data file before fetching new messages. **Warning**: This action deletes the existing data and can’t be undone. You’ll be prompted for confirmation when using this flag.

**Example Usage**:
```bash
python3 query.py --reset --limit 100
```

This command resets the data file (after user confirmation) and fetches up to 100 messages.

### 💾 File Manager (`filemanager.py`)

This is your file whisperer. It talks to Google Drive and makes sure your data’s where it needs to be.

**Key Tricks**:
- `open_file(file_id)`: Reads a file from Google Drive and hands it over as a DataFrame 📂
- `save_file(df, file_id)`: Saves your DataFrame back to the Drive 📥

## 🗣️ Hit Us Up

Got questions? Need help? Want to chat? Reach out to ChatGPT at NiUnaLineaMia@ascoIAperoqueUtil.caca. Let’s make something awesome together. 💬
