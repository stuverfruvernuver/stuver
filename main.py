import asyncio
import os
import requests
import websockets
from discord_webhook import DiscordWebhook
from datetime import datetime

KICK_AUTH_TOKEN = os.getenv("KICK_AUTH_TOKEN")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
CHANNEL_NAME = "streameruniversitario"

async def connect_to_chat():
    """Conectar al chat de Kick y saludar al inicio del stream"""
    channel_id = await get_channel_id(CHANNEL_NAME)
    
    # Conectar al chat usando websockets y tu cuenta de Kick
    async with websockets.connect(f"wss://kick.com/api/v2/channels/{channel_id}/chat?token={KICK_AUTH_TOKEN}") as websocket:
        await websocket.send('{"type":"hello"}')  # Enviar saludo inicial
        await websocket.send('{"type":"join"}')  # Unirse al canal

        # Esperar notificaciones del stream
        while True:
            message = await websocket.recv()
            if "stream" in message and "started" in message:
                await send_discord_notification("El stream ha comenzado")
                await send_discord_reminders()  # Enviar recordatorios cada 10 min
            elif "stream" in message and "ended" in message:
                await send_discord_notification("El stream ha terminado")
                break  # Detener cuando termine el stream

async def get_channel_id(channel_name):
    """Obtener el ID del canal de Kick por su nombre"""
    url = f"https://kick.com/api/v2/channels/{channel_name}"
    headers = {"Authorization": f"Bearer {KICK_AUTH_TOKEN}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json().get("id")
    else:
        raise Exception("No se pudo obtener el ID del canal")

async def send_discord_notification(message):
    """Enviar notificación a Discord"""
    webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL, content=message)
    webhook.execute()

async def send_discord_reminders():
    """Enviar recordatorios cada 10 minutos mientras el stream esté activo"""
    while True:
        await asyncio.sleep(600)  # 10 minutos
        await send_discord_notification(f"Recordatorio: el stream sigue activo. {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
