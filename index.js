import { createClient } from "kick-js";
import "dotenv/config";
import axios from "axios";

const CHANNEL = "Streameruniversitario";
const client = createClient(CHANNEL, { logger: true });

let streamLive = false;
let startTime = null;

client.login({
  type: "login",
  credentials: {
    username: process.env.KICK_USERNAME,
    password: process.env.KICK_PASSWORD,
    otp_secret: process.env.KICK_OTP_SECRET,
  },
});

function sendDiscordNotification(message) {
  axios.post(process.env.DISCORD_WEBHOOK_URL, { content: message }).catch(err => {
    console.error("[LOG] Error al enviar a Discord:", err.response?.data || err.message);
  });
}

client.on("ready", () => {
  console.log(`Bot listo y conectado como ${client.user?.tag}`);
  sendDiscordNotification(`Bot conectado como **${client.user?.tag}** al canal **${CHANNEL}**.`);
});

client.on("LiveStreamStart", () => {
  console.log("[LOG] ¡El stream ha comenzado!");
  streamLive = true;
  startTime = Date.now();
  client.sendMessage("Hola!");
  sendDiscordNotification("¡El stream ha comenzado!");
});

client.on("LiveStreamEnd", () => {
  console.log("[LOG] El stream ha terminado.");
  streamLive = false;
  client.sendMessage(":Bwop:");
  sendDiscordNotification("El stream ha terminado.");
});

setInterval(() => {
  if (streamLive && startTime) {
    const mins = Math.floor((Date.now() - startTime) / 60000);
    sendDiscordNotification(`El bot sigue en línea después de ${mins} minutos.`);
    client.sendMessage(":Bwop:");
  }
}, 600000);
