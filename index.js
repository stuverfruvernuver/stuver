import { createClient } from "./kick-js/dist/index.js"; // Asegúrate que esta ruta apunte al archivo correcto
import dotenv from "dotenv";
import fetch from "node-fetch";

dotenv.config();

const client = createClient(process.env.KICK_CHANNEL, {
  logger: true,
  readOnly: false,
});

const sendDiscordWebhook = async (message) => {
  try {
    await fetch(process.env.DISCORD_WEBHOOK_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        content: message,
        username: "KickBot",
        avatar_url: "https://preview.redd.it/60ti7xezkdix.jpg",
      }),
    });
  } catch (err) {
    console.error("[LOG] Error enviando al webhook de Discord:", err);
  }
};

let online = false;
let lastCheck = Date.now();

client.login({
  type: "login",
  credentials: {
    username: process.env.KICK_USERNAME,
    password: process.env.KICK_PASSWORD,
    otp_secret: process.env.KICK_OTP_SECRET,
  },
});

client.on("ready", async () => {
  console.log(`[LOG] Bot conectado como ${client.user?.username}`);
  await sendDiscordWebhook(`Bot conectado como **${client.user?.username}** al canal **${process.env.KICK_CHANNEL}**.`);

  setInterval(async () => {
    try {
      const info = await client.channel();
      if (info?.livestream) {
        if (!online) {
          console.log("[LOG] Stream ha comenzado");
          await client.sendMessage("Hola!");
          await sendDiscordWebhook(`El stream de ${process.env.KICK_CHANNEL} ha comenzado.`);
          online = true;
        } else {
          const minutes = Math.floor((Date.now() - lastCheck) / 60000);
          if (minutes >= 10) {
            await client.sendMessage(":Bwop:");
            await sendDiscordWebhook(`El bot sigue activo en el stream (${minutes} minutos en línea).`);
            lastCheck = Date.now();
          }
        }
      } else {
        if (online) {
          console.log("[LOG] Stream ha terminado");
          await sendDiscordWebhook(`El stream de ${process.env.KICK_CHANNEL} ha terminado.`);
          online = false;
        }
      }
    } catch (err) {
      console.error("[LOG] Error al revisar el estado del stream:", err);
    }
  }, 10 * 1000); // revisar cada 10 segundos
});
