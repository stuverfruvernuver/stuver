import os
import json
import asyncio
import websockets
import cloudscraper
from discord_webhook import DiscordWebhook

# Usa cloudscraper para evitar bloqueos de Cloudflare
scraper = cloudscraper.create_scraper()

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
KICK_AUTH_TOKEN = os.environ.get("KICK_AUTH_TOKEN")
STREAMER_NAME = "streameruniversitario"

def get_channel_id(channel_name):
    url = f"https://kick.com/api/v2/channels/{channel_name}"
    response = scraper.get(url)

    if response.status_code != 200:
        raise Exception("No se pudo obtener el ID del canal (Cloudflare)")

    data = response.json()
    return data.get("id")

async def connect_to_chat():
    channel_id = get_channel_id(STREAMER_NAME)
    uri = f"wss://chat.kick.com/socket.io/?EIO=4&transport=websocket"
    
    async with websockets.connect(uri) as websocket:
        await websocket.send('40')

        await asyncio.sleep(1)
        await websocket.send(f'42["join_channel",{{"channel_id":{channel_id}}}]')

        send_discord_message("Bot conectado al chat de Kick")

        while True:
            message = await websocket.recv()
            if "user joined" in message:
                print(f"[JOIN] {message}")
            elif "message" in message:
                print(f"[MSG] {message}")

def send_discord_message(content):
    if DISCORD_WEBHOOK_URL:
        webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL, content=content)
        webhook.execute()
