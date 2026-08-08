export function createStream(onMessage) {
    try {
        const WS_BASE = import.meta.env.VITE_WS_BASE || 'wss://sera-julius-platform-backend.onrender.com'
        const API_KEY = import.meta.env.VITE_API_KEY ?? 'sera-demo-2026'
        const WS_URL = `${WS_BASE}/api/ws/stream?api_key=${encodeURIComponent(API_KEY)}`
        
        const ws = new WebSocket(WS_URL)
        ws.onmessage = (e) => {
            try {
                const data = JSON.parse(e.data)
                onMessage(data)
            } catch {}
        }
        ws.onerror = () => {
            // Silently suppress WebSocket dev-server proxy errors
        }
        ws.onclose = () => {
            // Silently handled
        }
        return ws
    } catch (e) {
        return null;
    }
}
