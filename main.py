import asyncio
import json
import os

from telethon import TelegramClient, events

#this script gets the channel's messages/media in realtime

#create a Telegram App
# Account credentials
api_id = 00000000 #telegram app api_id
api_hash = 'app api_hash' #telegram app api_hash

# Target channel
channel_username = '@channel_name'  #replace {@channel_name} with the channel name or ID
media_dir = 'downloaded_media' #just one folder that holds media
os.makedirs(media_dir, exist_ok=True)

# JSON file to save message data
json_file = 'messages.json'

# Ensure the JSON file exists and starts as an empty list if not present
if not os.path.exists(json_file):
    with open(json_file, 'w') as f:
        json.dump([], f)

# Create the Telegram client
client = TelegramClient('session_name', api_id, api_hash)

@client.on(events.NewMessage(chats=channel_username))
async def new_message_listener(event):
    message = event.message
    result = {
        "channel": channel_username,
        "message_id": message.id,
        "date": message.date.isoformat(),
        "text": message.message or ""
    }

    # If message contains media, download it
    if message.media:
        media_path = os.path.join(media_dir, f"{message.id}")
        downloaded_path = await message.download_media(file=media_path)
        if downloaded_path:
            result["media_file"] = downloaded_path
            print(f"Media downloaded to {downloaded_path}")
        else:
            print("Failed to download media.")

    # Load existing data
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Append new message result
    data.append(result)

    # Write updated data back to JSON file
    with open(json_file, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Also print to console
    print(json.dumps(result, ensure_ascii=False, indent=2))

async def main():
    await client.start()
    print(f"Listening for new messages in {channel_username}")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
