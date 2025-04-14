import os
import time
import asyncio
import websockets
import requests
from discord_webhook import DiscordWebhook
from flask import Flask
from threading import Thread

KICK_SESSION_TOKEN = os.getenv("KICK_SESSION_TOKEN")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
CHANNEL_NAME = "streameruniversitario"
API_BASE = "https://kick.com/api/v2/channels/"

app = Flask(__name__)
start_time = None
is_live = False

def send_discord_message(content):
    webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL, content=content)
    webhook.execute()

def get_channel_id(channel_name):
    res = requests.get(API_BASE + channel_name)
    if res.status_code == 200:
        return res.json()["id"]
    return None

def is_stream_live(channel_name):
    res = requests.get(API_BASE + channel_name)
    if res.status_code == 200:
        return res.json()["livestream"] is not None
    return False

async def connect_to_chat(channel_id):
    url = f"wss://chat.kick.com/{channel_id}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://kick.com",
        "Cookie": f"__Secure-next-auth.session-token={KICK_SESSION_TOKEN}"
    }
    async with websockets.connect(url, extra_headers=headers) as ws:
        await ws.send('{"event":"join","data":{"room":"channel_{}"}}'.format(channel_id))
        await ws.send('{"event":"message","data":{"content":":Bwop:"}}')  # Saludo inicial

        while True:
            await asyncio.sleep(600)  # Cada 10 minutos
            await ws.send('{"event":"message","data":{"content":":Bwop:"}}')

def format_uptime(seconds):
    mins, secs = divmod(int(seconds), 60)
    hours, mins = divmod(mins, 60)
    return f"{hours:02d}:{mins:02d}:{secs:02d}"

def monitor_stream():
    global start_time, is_live
    channel_id = get_channel_id(CHANNEL_NAME)
    if not channel_id:
        print("Error: No se pudo obtener el ID del canal.")
        return

    while True:
        live = is_stream_live(CHANNEL_NAME)
        if live and not is_live:
            is_live = True
            start_time = time.time()
            send_discord_message("¡El stream ha comenzado!")
            asyncio.run(connect_to_chat(channel_id))
        elif not live and is_live:
            is_live = False
            send_discord_message("El stream ha terminado.")
        elif is_live:
            uptime = time.time() - start_time
            send_discord_message(f"Stream activo: {format_uptime(uptime)}")
        time.sleep(600)  # Verifica cada 10 minutos

@app.route('/')
def home():
    return "Kick bot está corriendo."

if __name__ == '__main__':
    Thread(target=monitor_stream).start()
    app.run(host="0.0.0.0", port=10000)
