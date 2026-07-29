export function createStream(onMessage) {
    try {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const host = window.location.host
        const WS_BASE = import.meta.env.VITE_WS_BASE ?? `${protocol}//${host}`
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