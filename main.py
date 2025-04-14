import time
import threading
import requests
from flask import Flask
from discord_webhook import DiscordWebhook
import websockets
import asyncio

# Variables de entorno (asegurarte de que estén en tu servidor de Render o en el archivo .env)
import os

KICK_AUTH_TOKEN = os.getenv("KICK_AUTH_TOKEN")  # Token de autenticación para Kick
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")  # URL del webhook de Discord
CHANNEL_NAME = "streameruniversitario"  # Nombre del canal de Kick

# Crear la app de Flask
app = Flask(__name__)

# Función que consulta si el stream está activo
async def check_stream_status():
    while True:
        # Usamos websockets o la API de Kick para verificar si el stream está activo
        # Aquí va la lógica para verificar el stream en Kick (puedes basarlo en la API o websockets)
        print("Verificando el estado del stream...")
        stream_active = True  # Esto es solo un ejemplo, deberías poner la lógica real aquí

        if stream_active:
            send_discord_notification("El stream ha comenzado!")
        else:
            send_discord_notification("El stream ha terminado!")

        await asyncio.sleep(600)  # Revisa cada 10 minutos

# Función para enviar notificación a Discord
def send_discord_notification(message):
    webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL, content=message)
    webhook.execute()

# Función principal del bot que interactúa con Kick
def start_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(check_stream_status())

# Ruta principal de Flask
@app.route('/')
def home():
    return 'Bot de Kick está activo y funcionando...'

# Iniciar Flask y el bot
if __name__ == "__main__":
    # Iniciar el bot en un hilo separado
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.start()

    # Iniciar el servidor Flask en el puerto 10000
    app.run(host="0.0.0.0", port=10000)
