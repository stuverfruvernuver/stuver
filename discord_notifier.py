import time
import os
import requests

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
AVATAR_URL = os.environ.get("AVATAR_URL", "")
CHANNEL_NAME = os.environ.get("CHANNEL_NAME", "streameruniversitario")

start_time = time.time()

def send_discord_ping():
    try:
        elapsed_seconds = int(time.time() - start_time)
        minutes, seconds = divmod(elapsed_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        uptime = f"{hours}h {minutes}m {seconds}s"
        payload = {
            "content": f"✅ Bot activo en **{CHANNEL_NAME}** (cuenta: johndyfire)\n⏱ Activo por: `{uptime}`",
            "username": "KickBot",
            "avatar_url": AVATAR_URL
        }
        requests.post(DISCORD_WEBHOOK_URL, json=payload)
        print(f"[Ping Discord] Activo por: {uptime}")
    except Exception as e:
        print("Error en ping Discord:", e)

async def periodic_discord_pings():
    while True:
        send_discord_ping()
        await asyncio.sleep(600)
