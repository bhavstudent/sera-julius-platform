import React, { useEffect, useState } from 'react'

export default function ThreatAlertBanner() {
  const [activeThreat, setActiveThreat] = useState(null)
  const [muted, setMuted] = useState(() => localStorage.getItem('sera_mute_threats') === 'true')
  const [dismissedKeys, setDismissedKeys] = useState(() => {
    try {
      const saved = localStorage.getItem('sera_dismissed_threats')
      return saved ? new Set(JSON.parse(saved)) : new Set()
    } catch {
      return new Set()
    }
  })

  useEffect(() => {
    if (muted) return

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const wsUrl = `${protocol}//${host}/api/security/ws/threats?api_key=sera-demo-2026`

    let socket
    try {
      socket = new WebSocket(wsUrl)

      socket.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data)
          if (msg.type === 'threat_alert' && msg.data) {
            const data = msg.data
            // Unique key by IP + Title to identify unique threats like an email subject
            const threatKey = `${data.ip || ''}_${data.title || ''}`.trim()

            // If user has already dismissed or marked this threat as read, DO NOT pop up again
            if (dismissedKeys.has(threatKey)) {
              return
            }

            // Set single active threat notification (Email Preview Style)
            setActiveThreat({
              key: threatKey,
              id: Date.now(),
              receivedAt: new Date().toLocaleTimeString(),
              ...data
            })
          }
        } catch (err) {
          console.error('[ThreatStream] Parse error:', err)
        }
      }

      socket.onerror = () => {}
    } catch (e) {}

    return () => {
      if (socket) socket.close()
    }
  }, [muted, dismissedKeys])

  // Mark as Read & Stop Future Popups for this threat
  const handleMarkAsRead = () => {
    if (!activeThreat) return
    const keyToDismiss = activeThreat.key
    setDismissedKeys(prev => {
      const updated = new Set(prev)
      updated.add(keyToDismiss)
      try {
        localStorage.setItem('sera_dismissed_threats', JSON.stringify(Array.from(updated)))
      } catch {}
      return updated
    })
    setActiveThreat(null)
  }

  // Toggle Mute All Popups
  const toggleMute = () => {
    const nextMute = !muted
    setMuted(nextMute)
    localStorage.setItem('sera_mute_threats', String(nextMute))
    if (nextMute) {
      setActiveThreat(null)
    }
  }

  if (muted || !activeThreat) return null

  return (
    <div style={{
      position: 'fixed',
      top: '16px',
      right: '20px',
      zIndex: 99999,
      maxWidth: '460px',
      width: 'calc(100% - 40px)',
      animation: 'slideInRight 0.3s cubic-bezier(0.16, 1, 0.3, 1)'
    }}>
      <div style={{
        background: 'linear-gradient(135deg, rgba(12, 16, 32, 0.96) 0%, rgba(20, 26, 48, 0.95) 100%)',
        border: '1px solid rgba(255, 42, 32, 0.5)',
        boxShadow: '0 12px 35px rgba(0,0,0,0.8), 0 0 20px rgba(255, 42, 32, 0.25)',
        borderRadius: '10px',
        backdropFilter: 'blur(16px)',
        overflow: 'hidden',
        color: '#ffffff'
      }}>
        {/* Email Header Bar */}
        <div style={{
          background: 'rgba(255, 42, 32, 0.12)',
          padding: '10px 14px',
          borderBottom: '1px solid rgba(255, 42, 32, 0.25)',
          display: 'flex',
          justify: 'space-between',
          alignItems: 'center',
          fontSize: '11px',
          fontFamily: 'monospace'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '13px' }}>📩</span>
            <span style={{ fontWeight: 'bold', color: '#ff5e3a', letterSpacing: '0.5px' }}>
              SECURITY INBOX // NEW ALERT
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ color: '#94a3b8', fontSize: '10px' }}>{activeThreat.receivedAt}</span>
            <button
              onClick={toggleMute}
              title="Mute all threat popups"
              style={{
                background: 'rgba(255,255,255,0.06)',
                border: '1px solid rgba(255,255,255,0.15)',
                color: '#cbd5e1',
                padding: '2px 8px',
                borderRadius: '4px',
                fontSize: '10px',
                cursor: 'pointer'
              }}
            >
              🔕 Mute
            </button>
          </div>
        </div>

        {/* Notification Body */}
        <div style={{ padding: '14px 16px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 'bold', fontSize: '13px' }}>
            <span style={{ color: activeThreat.severity === 'CRITICAL' ? '#ff2a20' : '#ffb340' }}>
              {activeThreat.title || 'CRITICAL THREAT DETECTED'}
            </span>
          </div>

          <p style={{ margin: 0, fontSize: '12px', color: '#cbd5e1', lineHeight: '1.5' }}>
            {activeThreat.detail}
          </p>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '4px', flexWrap: 'wrap', gap: '8px' }}>
            {activeThreat.ip && (
              <span className="mono" style={{
                fontSize: '11px',
                background: 'rgba(255, 42, 32, 0.1)',
                border: '1px solid rgba(255, 42, 32, 0.3)',
                color: '#ff5e3a',
                padding: '2px 8px',
                borderRadius: '4px'
              }}>
                Target: {activeThreat.ip}
              </span>
            )}

            {/* Email-Style Action Button: Mark Read & Stop Popups */}
            <button
              onClick={handleMarkAsRead}
              style={{
                background: 'linear-gradient(135deg, #ff2a20 0%, #ff003c 100%)',
                color: '#ffffff',
                border: 'none',
                padding: '6px 14px',
                borderRadius: '6px',
                fontSize: '11px',
                fontWeight: 'bold',
                cursor: 'pointer',
                boxShadow: '0 0 12px rgba(255, 42, 32, 0.4)',
                marginLeft: 'auto'
              }}
            >
              ✓ Mark Read & Stop Popups
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
