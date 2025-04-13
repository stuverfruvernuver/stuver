import asyncio
import websockets
import json
import time
import os
import cloudscrapper
from discord_notifier import periodic_discord_pings
from stream_checker import periodic_stream_checks

AUTH_TOKEN = os.environ.get("KICK_AUTH_TOKEN")
CHANNEL_NAME = "Streameruniversitario"
WS_URI = "wss://chat.kick.com"

def get_channel_id(channel_name):
    scraper = cloudscraper.create_scraper()
    url = f"https://kick.com/api/v2/channels/{channel_name}"
    response = scraper.get(url)
    if response.status_code == 200:
        return response.json()["id"]
    else:
        raise Exception("No se pudo obtener el ID del canal (Cloudflare)")

async def connect_to_chat():
    channel_id = get_channel_id(CHANNEL_NAME)
    async with websockets.connect(WS_URI) as ws:
        join_msg = {
            "event": "phx_join",
            "topic": f"chatrooms:{channel_id}",
            "payload": {"token": AUTH_TOKEN},
            "ref": "1"
        }
        await ws.send(json.dumps(join_msg))
        print(f"Conectado al chat de '{CHANNEL_NAME}'")

        async def listener():
            while True:
                raw_msg = await ws.recv()
                try:
                    data = json.loads(raw_msg)
                    if data.get("event") == "message.new":
                        msg = data["payload"]["message"]
                        user = msg["sender"]["username"]
                        text = msg["content"]
                        print(f"{user}: {text}")
                except Exception as e:
                    print("Error leyendo mensaje:", e)

        async def send_message_loop():
            while True:
                msg = input("Escribe tu mensaje (o 'salir'): ")
                if msg.lower() == "salir":
                    break
                send_payload = {
                    "event": "message.send",
                    "topic": f"chatrooms:{channel_id}",
                    "payload": {"content": msg},
                    "ref": str(int(time.time()))
                }
                await ws.send(json.dumps(send_payload))

        await asyncio.gather(
            listener(),
            send_message_loop(),
            periodic_discord_pings(),
            periodic_stream_checks()
        )
