import os
import asyncio
import websockets
import requests
import json
from discord_webhook import DiscordWebhook
from datetime import datetime

CHANNEL_NAME = "streameruniversitario"
KICK_AUTH_TOKEN = os.getenv("KICK_AUTH_TOKEN")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

GREETING_SENT = False
STREAM_LIVE = False

def get_channel_info(channel_name):
    url = f"https://kick.com/api/v2/channels/{channel_name}"
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if res.status_code == 200:
        data = res.json()
        return {
            "id": data["id"],
            "is_live": data["livestream"] is not None,
        }
    raise Exception("No se pudo obtener información del canal")

def send_discord_message(content):
    if DISCORD_WEBHOOK:
        try:
            webhook = DiscordWebhook(url=DISCORD_WEBHOOK, content=content)
            webhook.execute()
        except Exception as e:
            print(f"Error al enviar a Discord: {e}")

async def monitor_stream():
    global STREAM_LIVE, GREETING_SENT
    channel_info = get_channel_info(CHANNEL_NAME)
    channel_id = channel_info["id"]

    while True:
        try:
            info = get_channel_info(CHANNEL_NAME)
            is_live = info["is_live"]

            if is_live and not STREAM_LIVE:
                STREAM_LIVE = True
                GREETING_SENT = False
                send_discord_message(f"El stream de **{CHANNEL_NAME}** ha comenzado.")
                asyncio.create_task(join_chat(channel_id))
            elif not is_live and STREAM_LIVE:
                STREAM_LIVE = False
                send_discord_message(f"El stream de **{CHANNEL_NAME}** ha terminado.")
            elif is_live:
                send_discord_message(f"{datetime.now().strftime('%H:%M:%S')}: {CHANNEL_NAME} sigue en directo.")

            await asyncio.sleep(600)  # 10 minutos
        except Exception as e:
            print(f"Error monitoreando stream: {e}")
            await asyncio.sleep(30)

async def join_chat(channel_id):
    global GREETING_SENT

    uri = f"wss://chat.kick.com/chat/v2?channel_id={channel_id}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Authorization": f"Bearer {KICK_AUTH_TOKEN}"
    }

    try:
        async with websockets.connect(uri, extra_headers=headers) as websocket:
            while not GREETING_SENT:
                greeting = {
                    "id": 1,
                    "type": "message",
                    "data": {
                        "content": "Hola!",
                        "channel_id": channel_id
                    }
                }
                await websocket.send(json.dumps(greeting))
                GREETING_SENT = True
                break
    except Exception as e:
        print(f"Error en el chat: {e}")

if __name__ == "__main__":
    asyncio.run(monitor_stream())
