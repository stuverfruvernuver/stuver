import asyncio
import os
import time
import requests
from flask import Flask
from discord_webhook import DiscordWebhook
import websockets
import json

app = Flask(__name__)
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
KICK_USERNAME = os.getenv("KICK_USERNAME")  # Tu nombre de usuario de Kick
KICK_PASSWORD = os.getenv("KICK_PASSWORD")  # Tu contraseña de Kick
CHANNEL_NAME = "Streameruniversitario"

start_time = time.time()

# Función para obtener el token de acceso
def get_kick_token(username, password):
    login_url = "https://kick.com/api/v1/login"  # La URL de autenticación
    login_data = {
        "username": username,
        "password": password
    }
    try:
        response = requests.post(login_url, json=login_data)
        if response.ok:
            data = response.json()
            return data.get("access_token")
        else:
            print("[LOG] No se pudo obtener el token de acceso:", response.status_code, response.text)
            return None
    except Exception as e:
        print("[LOG] Error al obtener el token:", str(e))
        return None

# Obtener el token de acceso automáticamente
KICK_ACCESS_TOKEN = get_kick_token(KICK_USERNAME, KICK_PASSWORD)
if KICK_ACCESS_TOKEN is None:
    print("[LOG] Error al obtener el token de acceso, el bot no puede continuar.")
    exit(1)

headers = {
    "Authorization": f"Bearer {KICK_ACCESS_TOKEN}",
    "User-Agent": "Mozilla/5.0"
}

def notify_discord(message):
    try:
        webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL, content=message,
        username = "Bwop!", 
        avatar_url = "https://preview.redd.it/60ti7xezkdix.jpg?width=640&crop=smart&auto=webp&s=d32d884e61930070549b00d96c5607209c3f8002" )
        response = webhook.execute()
        if not response.ok:
            print("[LOG] Falló el envío a Discord:", response.status_code, response.text)
    except Exception as e:
        print("[LOG] Error al enviar al webhook de Discord:", str(e))


def get_authenticated_username():
    try:
        # Usamos el token para obtener los detalles del usuario
        response = requests.get("https://kick.com/api/v1/users/me", headers=headers)
        if response.ok:
            data = response.json()
            return data.get("username")
        else:
            print("[LOG] No se pudo obtener el nombre de usuario de Kick")
            return "Desconocido"
    except Exception as e:
        print("[LOG] Error al obtener el usuario Kick:", str(e))
        return "Desconocido"


async def connect_to_chat():
    try:
        url = f"wss://chat.kick.com/socket.io/?channel={CHANNEL_NAME}&EIO=4&transport=websocket"
        async with websockets.connect(url) as ws:
            print(f"[LOG] Conectado al chat de {CHANNEL_NAME}")
            await ws.send("40")  # protocolo de conexión con socket.io
            await ws.send('42["join", {"channel": "' + CHANNEL_NAME + '"}]')

            await ws.send('42["message", {"content": "Hola!"}]')  # mensaje al empezar stream

            while True:
                elapsed = int(time.time() - start_time)
                if elapsed % 600 < 5:  # cada 10 minutos
                    try:
                        await ws.send('42["message", {"content": ":Bwop:"}]')
                        notify_discord(f"El bot sigue en línea después de {elapsed // 60} minutos.")
                        await asyncio.sleep(5)
                    except Exception as e:
                        print("[LOG] No se pudo enviar el mensaje o notificar en Discord:", e)
                await asyncio.sleep(1)
    except Exception as e:
        print("[LOG] Error en la conexión al chat:", e)


@app.route('/')
def index():
    return "Bot de Kick activo."


if __name__ == '__main__':
    username = get_authenticated_username()
    notify_discord(f"Bot conectado como **{username}** al canal **{CHANNEL_NAME}**.")
    loop = asyncio.get_event_loop()
    loop.create_task(connect_to_chat())
    app.run(host="0.0.0.0", port=10000)
