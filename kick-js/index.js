export function createClient(channel, options) {
  return {
    user: { username: "KickUser123" },
    login: async () => console.log("[kick-js] Autenticado"),
    on: (event, callback) => {
      if (event === "ready") setTimeout(callback, 1000);
    },
    channel: async () => ({
      livestream: Math.random() > 0.3 ? { status: "live" } : null
    }),
    sendMessage: async (msg) => console.log("[kick-js] Mensaje enviado:", msg)
  };
}
