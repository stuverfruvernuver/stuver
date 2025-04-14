import asyncio
import requests
import websockets
import time
import os
from discord_webhook import DiscordWebhook

# Variables de entorno (se obtienen de un archivo `.env` o las defines directamente)
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
KICK_USERNAME = os.getenv("KICK_USERNAME")  # Tu nombre de usuario de Kick
KICK_PASSWORD = os.getenv("KICK_PASSWORD")  # Tu contraseña de Kick
CHANNEL_NAME = "Streameruniversitario"

# Configuración de WebSocket
start_time = time.time()

# Función para obtener el token (inspirado en kick-js)
def authenticate_kick(username, password):
    # En `kick-js`, se realiza una autenticación básica con username y password.
    # Aquí usaremos una simulación (deberías reemplazarlo con la API correcta o flujo OAuth)
    
    auth_url = "https://kick.com/api/v1/authenticate"  # Endpoint hipotético
    payload = {"username": username, "password": password}
    
    response = requests.post(auth_url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        return data['token']  # Suponiendo que la API devuelve un 'token' en JSON
    else:
        print("[LOG] Error de autenticación:", response.text)
        return None

# Función para notificar a Discord
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

# Función para obtener el nombre de usuario autenticado
def get_authenticated_username(token):
    # Supongamos que la API de Kick tiene un endpoint para obtener el usuario autenticado
    user_url = "https://kick.com/api/v1/user"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(user_url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return data.get("username")
    else:
        print("[LOG] No se pudo obtener el nombre de usuario")
        return "Desconocido"

# Función para conectarse al chat usando WebSocket
async def connect_to_chat(token):
    try:
        url = f"wss://chat.kick.com/socket.io/?channel={CHANNEL_NAME}&EIO=4&transport=websocket"
        async with websockets.connect(url) as ws:
            print(f"[LOG] Conectado al chat de {CHANNEL_NAME}")
            await ws.send("40")  # protocolo de conexión con socket.io
            await ws.send(f'42["join", {{"channel": "{CHANNEL_NAME}"}}]')

            await ws.send('42["message", {"content": "¡Hola! Stream comenzado."}]')  # mensaje al empezar stream

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

# Función principal del bot
def run_bot():
    token = authenticate_kick(KICK_USERNAME, KICK_PASSWORD)
    if not token:
        print("[LOG] No se pudo autenticar. El bot no puede continuar.")
        return
    
    username = get_authenticated_username(token)
    notify_discord(f"Bot conectado como **{username}** al canal **{CHANNEL_NAME}**.")
    
    # Ejecutar el WebSocket en un bucle asincrónico
    loop = asyncio.get_event_loop()
    loop.create_task(connect_to_chat(token))
    loop.run_forever()

if __name__ == '__main__':
    run_bot()
