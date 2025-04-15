export function createClient(channel, options) {
    const user = { username: "KickUser123" };
  
    const login = (credentials) => {
      console.log(`[LOG] Iniciando sesión como ${credentials.credentials.username}`);
    };
  
    const on = (event, callback) => {
      if (event === "ready") {
        setTimeout(() => {
          callback();
        }, 1000); // Simula conexión
      }
    };
  
    const sendMessage = async (message) => {
      console.log(`[CHAT] ${user.username}: ${message}`);
    };
  
    const channelInfo = async () => {
      const isLive = Math.random() > 0.5; // Simula el estado aleatorio del stream
      return {
        livestream: isLive ? { title: "En vivo!" } : null
      };
    };
  
    return {
      login,
      on,
      sendMessage,
      channel: channelInfo,
      user
    };
  }