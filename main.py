import asyncio
import json
import time
from chat import connect_to_chat
from discord_notifier import send_discord_ping, periodic_discord_pings
from stream_checker import periodic_stream_checks

with open("config.json") as f:
    config = json.load(f)

CHANNEL_NAME = config["channel_name"]

if __name__ == "__main__":
    send_discord_ping()
    asyncio.run(connect_to_chat(CHANNEL_NAME))
