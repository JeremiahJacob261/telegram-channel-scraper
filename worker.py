import asyncio
import json
import os
from telethon import TelegramClient, events

#this script get the last {scrap_length} messages/media of the channel

# Account credentials
api_id = 0000000   #replace with app's api_id
api_hash = 'app api_hash' 

# Target channel
channel_username = '@channel_name'  # Change to your channel
scrap_length = 10 #the number of messages to get

media_dir = 'downloaded_media'  # Folder for downloaded media
os.makedirs(media_dir, exist_ok=True)

# JSON file to save message data
json_file = 'messages.json'

# Ensure JSON file exists, initialize as empty list if not
if not os.path.exists(json_file):
    with open(json_file, 'w') as f:
        json.dump([], f)

# Create Telegram client
client = TelegramClient('session_name', api_id, api_hash)


async def main():
    await client.start()

    # Load existing data from JSON file
    with open(json_file, 'r') as f:
        data = json.load(f)
    existing_ids = {msg['message_id'] for msg in data if 'message_id' in msg}

    # Function to process messages (historical and new)
    async def process_message(message):
        if message.id in existing_ids:
            print(f"Message {message.id} already processed, skipping.")
            return
        result = {
            "channel": channel_username,
            "message_id": message.id,
            "date": message.date.isoformat(),
            "text": message.message or ""
        }
        # Download media if present
        if message.media:
            media_path = os.path.join(media_dir, f"{message.id}")
            downloaded_path = await message.download_media(file=media_path)
            if downloaded_path:
                result["media_file"] = downloaded_path
                print(f"Media downloaded to {downloaded_path}")
            else:
                print(f"Failed to download media for message {message.id}.")
        # Append to data and update JSON file
        data.append(result)
        existing_ids.add(message.id)
        with open(json_file, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    # Fetch last 10 messages
    print(f"Fetching last 10 messages from {channel_username}")
    messages = await client.get_messages(channel_username, limit=scrap_length)
    messages.sort(key=lambda m: m.id)  # Sort chronologically by ID
    for message in messages:
        await process_message(message)

    # Event handler for new messages
    @client.on(events.NewMessage(chats=channel_username))
    async def new_message_listener(event):
        await process_message(event.message)

    print(f"Listening for new messages in {channel_username}")
    await client.run_until_disconnected()


if __name__ == '__main__':
    asyncio.run(main())
