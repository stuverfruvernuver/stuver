import requests
import json
import asyncio

with open("config.json") as f:
    config = json.load(f)

DISCORD_WEBHOOK_URL = config["discord_webhook_url"]
AVATAR_URL = config.get("avatar_url", "")
CHANNEL_NAME = config["channel_name"]

last_stream_status = None

def check_stream_status():
    global last_stream_status
    try:
        url = f"https://kick.com/api/v1/channels/{CHANNEL_NAME}"
        response = requests.get(url)
        if response.status_code == 200:
            is_live = response.json().get("livestream") is not None
            if last_stream_status is None:
                last_stream_status = is_live
            if is_live and not last_stream_status:
                payload = {
                    "content": f"🔴 ¡El canal **{CHANNEL_NAME}** ha empezado a transmitir!",
                    "username": "KickBot",
                    "avatar_url": AVATAR_URL
                }
                requests.post(DISCORD_WEBHOOK_URL, json=payload)
            elif not is_live and last_stream_status:
                payload = {
                    "content": f"⚫ El canal **{CHANNEL_NAME}** terminó su transmisión.",
                    "username": "KickBot",
                    "avatar_url": AVATAR_URL
                }
                requests.post(DISCORD_WEBHOOK_URL, json=payload)
            last_stream_status = is_live
    except Exception as e:
        print("Error revisando estado del stream:", e)

async def periodic_stream_checks():
    while True:
        check_stream_status()
        await asyncio.sleep(60)
