import os
import time
import requests
import asyncio
import json
from flask import Flask, redirect
from discord_webhook import DiscordWebhook
import websockets
from urllib.parse import urlencode
from requests.auth import HTTPBasicAuth

# Configuración
app = Flask(__name__)
CLIENT_ID = '01JRTHNAP1AE4S75524PEXN0DN'  # Reemplazar con tu client_id
CLIENT_SECRET = '0061627a12559ca2025a8e2202d9a4cbb89b3fed26c816c9869432a552d44f10'  # Reemplazar con tu client_secret
REDIRECT_URI = 'http://localhost:5000/callback'  # Reemplazar con tu redirect URI
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")  # URL del webhook de Discord
CHANNEL_NAME = "Streameruniversitario"
start_time = time.time()

# Headers comunes para las peticiones HTTP
headers = {
    "user-agent": "Mozilla/5.0"
}

def notify_discord(message):
    try:
        webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL, content=message,
                                 username="Bwop!", 
                                 avatar_url="https://preview.redd.it/60ti7xezkdix.jpg?width=640&crop=smart&auto=webp&s=d32d884e61930070549b00d96c5607209c3f8002")
        response = webhook.execute()
        if not response.ok:
            print("[LOG] Falló el envío a Discord:", response.status_code, response.text)
    except Exception as e:
        print("[LOG] Error al enviar al webhook de Discord:", str(e))

# Endpoint para iniciar el proceso de OAuth
@app.route('/login')
def login():
    authorization_url = f'https://kick.com/oauth/authorize?{urlencode({"client_id": CLIENT_ID, "redirect_uri": REDIRECT_URI, "response_type": "code", "scope": "chat:read chat:write"})}'
    return redirect(authorization_url)

# Endpoint para manejar la redirección después de la autenticación de OAuth
@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return "Error: No se obtuvo el código de autorización", 400

    # Intercambiar el código por el token de acceso
    token_url = 'https://kick.com/oauth/token'
    data = {
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    response = requests.post(token_url, data=data, auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET))
    
    if response.ok:
        token_data = response.json()
        access_token = token_data.get('access_token')
        if access_token:
            # Guardar el access token para su uso en futuras solicitudes
            os.environ['ACCESS_TOKEN'] = access_token
            notify_discord("Bot conectado exitosamente a Kick.")
            return "Autenticación exitosa. El bot está listo para interactuar con el chat."
        else:
            return "Error: No se obtuvo el token de acceso.", 400
    else:
        return f"Error al obtener el token: {response.status_code}", 400

def get_authenticated_username():
    access_token = os.getenv('ACCESS_TOKEN')
    if not access_token:
        return "Desconocido"

    try:
        headers["Authorization"] = f"Bearer {access_token}"
        response = requests.get("https://kick.com/api/v1/user", headers=headers)
        if response.ok:
            data = response.json()
            return data.get("username", "Desconocido")
        else:
            print("[LOG] No se pudo obtener el nombre de usuario de Kick")
            return "Desconocido"
    except Exception as e:
        print("[LOG] Error al obtener el usuario Kick:", str(e))
        return "Desconocido"

async def connect_to_chat():
    access_token = os.getenv('ACCESS_TOKEN')
    if not access_token:
        print("[LOG] No se pudo obtener el token de acceso.")
        return

    username = get_authenticated_username()
    print(f"[LOG] Conectado como {username} en el canal {CHANNEL_NAME}")
    
    try:
        url = f"wss://websockets.kick.com/viewer/v1/connect?token={access_token}"
        async with websockets.connect(url) as ws:
            print(f"[LOG] Conectado al chat de {CHANNEL_NAME}")
            await ws.send("40")  # Protocolo de conexión con socket.io
            await ws.send(f'42["join", {{"channel": "{CHANNEL_NAME}"}}]')
            await ws.send('42["message", {"content": "Hola!"}]')  # Enviar saludo al iniciar stream

            while True:
                elapsed = int(time.time() - start_time)
                if elapsed % 600 < 5:  # Cada 10 minutos
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
    if username != "Desconocido":
        notify_discord(f"Bot conectado como **{username}** al canal **{CHANNEL_NAME}**.")
    loop = asyncio.get_event_loop()
    loop.create_task(connect_to_chat())
    app.run(host="0.0.0.0", port=5000)
