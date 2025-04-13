import asyncio
from chat import connect_to_chat
from discord_notifier import send_discord_ping
from stream_checker import periodic_stream_checks

if __name__ == "__main__":
    send_discord_ping()
    asyncio.run(connect_to_chat())
