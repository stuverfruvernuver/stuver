import requests
import time
import json
import asyncio
import websockets
from flask import Flask
from threading import Thread
from discord_webhook import DiscordWebhook

app = Flask(__name__)

# Configuración
KICK_AUTH_TOKEN = "tu_token_aqui"
DISCORD_WEBHOOK_URL = "tu_discord_webhook_aqui"
CHANNEL_NAME = "Streameruniversitario"
BASE_URL = "https://kick.com/api/v2"
HEADERS = {
    "Authorization": f"Bearer {KICK_AUTH_TOKEN}",
    "User-Agent": "Mozilla/5.0"
}

# Tiempo de inicio del bot
start_time = time.time()

# Función para obtener el ID del canal
async def get_channel_id():
    url = f"{BASE_URL}/channels/{CHANNEL_NAME}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()["data"]["id"]
    else:
        raise Exception("No se pudo obtener el ID del canal")

# Función para enviar mensaje a Discord
def send_discord_notification(message):
    webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL, content=message)
    webhook.execute()

# Función principal para conectarse al chat
async def connect_to_chat():
    channel_id = await get_channel_id()
    uri = f"wss://kick.com/api/v2/stream/{channel_id}/chat"

    async with websockets.connect(uri) as websocket:
        # Unirse al chat y enviar "Hola!"
        await websocket.send(json.dumps({"op": 1, "d": {"type": "hello"}}))
        await websocket.send(json.dumps({"op": 1, "d": {"type": "join", "room": CHANNEL_NAME}}))
        await websocket.send(json.dumps({"op": 4, "d": {"type": "chat", "message": "Hola!"}}))
        print("Mensaje 'Hola!' enviado al chat.")
        send_discord_notification("El stream ha comenzado. Bot activo.")

        # Repetir cada 10 minutos
        while True:
            await websocket.send(json.dumps({
                "op": 4,
                "d": {
                    "type": "chat",
                    "message": ":Bwop:"
                }
            }))
            # Calcular el tiempo en minutos
            elapsed = int((time.time() - start_time) // 60)
            send_discord_notification(f":clock10: El bot lleva activo {elapsed} minuto(s).")
            print(f"Enviado mensaje :Bwop: al chat y notificación a Discord ({elapsed} min)")
            await asyncio.sleep(600)

# Ejecutar el bot en hilo separado
def start_bot():
    asyncio.run(main_bot())

async def main_bot():
    await connect_to_chat()

@app.route('/')
def home():
    return "El bot está activo."

@app.route('/start_bot')
def start():
    thread = Thread(target=start_bot)
    thread.start()
    return "Bot iniciado."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
