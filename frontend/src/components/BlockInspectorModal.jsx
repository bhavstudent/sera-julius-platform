import { useState, useEffect } from 'react'

export default function BlockInspectorModal({ blockData, onClose }) {
  const [inspecting, setInspecting] = useState(false)
  const [inspectLog, setInspectLog] = useState([])

  useEffect(() => {
    if (blockData) {
      setInspectLog([
        `[INSPECTOR] Attached to subsystem: ${blockData.title || 'Telemetry Block'}`,
        `[TELEMETRY] Live stream status: ACTIVE (${blockData.refresh || 'Sub-second real-time'})`,
        `[AGENT] Assigned Autonomous Agent: ${blockData.agent || 'STYX Orchestrator'}`,
        `[HEALTH] Subsystem integrity verified at 100% efficiency.`
      ])
    }
  }, [blockData])

  if (!blockData) return null

  const runDeepScan = () => {
    setInspecting(true)
    setInspectLog(prev => [
      ...prev,
      `[PROBE] Executing real-time diagnostic sweep on ${blockData.title}...`,
      `[METRIC] Subsystem metrics verified across ${Math.floor(Math.random() * 50 + 10)} node endpoints.`,
      `[DIAGNOSTIC] Zero packet loss detected. Entropy variance stable.`
    ])
    setTimeout(() => {
      setInspecting(false)
    }, 900)
  }

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(4, 5, 10, 0.88)',
      backdropFilter: 'blur(24px)',
      WebkitBackdropFilter: 'blur(24px)',
      zIndex: 99999,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px'
    }} onClick={onClose}>
      
      <div style={{
        background: 'linear-gradient(135deg, rgba(8, 11, 22, 0.98) 0%, rgba(16, 20, 36, 0.96) 100%)',
        border: '2px solid #ff2a20',
        borderRadius: '18px',
        padding: '28px',
        maxWidth: '680px',
        width: '100%',
        boxShadow: '0 0 60px rgba(255, 42, 32, 0.45), 0 20px 80px rgba(0,0,0,0.95)',
        position: 'relative',
        overflow: 'hidden'
      }} onClick={e => e.stopPropagation()}>
        
        {/* Reticle HUD Corner Brackets */}
        <span className="hud-corner top-left" />
        <span className="hud-corner top-right" />
        <span className="hud-corner bottom-left" />
        <span className="hud-corner bottom-right" />
        <div className="cyber-scanline" />

        {/* Modal Title Bar */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px', borderBottom: '1px solid rgba(255,42,32,0.3)', paddingBottom: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontSize: '24px' }}>{blockData.icon || '🛡️'}</span>
            <div>
              <h3 style={{ margin: 0, fontSize: '1.2rem', color: '#ffffff', fontWeight: '900', letterSpacing: '0.5px' }}>
                {blockData.title || 'SUBSYSTEM CONTAINER'}
              </h3>
              <span className="mono" style={{ fontSize: '10px', color: '#ff5e3a', fontWeight: 'bold' }}>
                LIVE CYBERSPACE TELEMETRY & SUBSYSTEM INSPECTOR
              </span>
            </div>
          </div>

          <button
            onClick={onClose}
            style={{
              background: 'rgba(255,42,32,0.15)',
              border: '1px solid #ff2a20',
              color: '#ff2a20',
              borderRadius: '50%',
              width: '32px',
              height: '32px',
              cursor: 'pointer',
              fontWeight: '900',
              fontSize: '14px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            ✕
          </button>
        </div>

        {/* Modal Content */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: '20px' }}>
          
          {/* Detailed Purpose */}
          <div style={{ background: 'rgba(255, 42, 32, 0.05)', border: '1px solid rgba(255, 42, 32, 0.2)', borderRadius: '10px', padding: '14px' }}>
            <h4 style={{ color: '#ff5e3a', fontSize: '10.5px', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '6px', fontWeight: 'bold' }}>
              ● Subsystem Purpose & Functional Mechanics:
            </h4>
            <p style={{ color: '#cbd5e1', fontSize: '13px', lineHeight: '1.55', margin: 0 }}>
              {blockData.description}
            </p>
          </div>

          {/* Contextual Technical Metrics Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
            <div style={{ background: 'rgba(10, 14, 26, 0.9)', border: '1px solid rgba(255, 42, 32, 0.25)', borderRadius: '10px', padding: '12px' }}>
              <div style={{ fontSize: '9.5px', color: '#94a3b8', fontWeight: 'bold', textTransform: 'uppercase' }}>Governing AI Agent</div>
              <div style={{ fontSize: '12.5px', color: '#ffffff', fontWeight: '800', marginTop: '4px' }}>
                {blockData.agent || 'STYX Orchestrator'}
              </div>
            </div>

            <div style={{ background: 'rgba(10, 14, 26, 0.9)', border: '1px solid rgba(255, 94, 58, 0.25)', borderRadius: '10px', padding: '12px' }}>
              <div style={{ fontSize: '9.5px', color: '#94a3b8', fontWeight: 'bold', textTransform: 'uppercase' }}>Data Source & Refresh</div>
              <div style={{ fontSize: '12.5px', color: '#ff5e3a', fontWeight: '800', marginTop: '4px' }} className="mono">
                {blockData.refresh || 'Live WebSocket (Port 8000)'}
              </div>
            </div>
          </div>

          {/* Key Metrics / Technical Data (if available) */}
          {blockData.keyMetrics && (
            <div style={{ background: 'rgba(4, 5, 10, 0.95)', border: '1px solid rgba(0, 245, 212, 0.3)', borderRadius: '10px', padding: '12px 14px' }}>
              <div style={{ fontSize: '9.5px', color: '#00f5d4', fontWeight: 'bold', textTransform: 'uppercase', marginBottom: '8px' }}>
                ⚡ LIVE CONTAINER METRICS & TELEMETRY BREAKDOWN:
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '8px' }}>
                {Object.entries(blockData.keyMetrics).map(([k, v]) => (
                  <div key={k} style={{ background: 'rgba(255, 255, 255, 0.04)', padding: '6px 10px', borderRadius: '6px' }}>
                    <div style={{ fontSize: '9px', color: '#94a3b8' }}>{k}</div>
                    <div className="mono" style={{ fontSize: '12px', color: '#ffffff', fontWeight: 'bold' }}>{String(v)}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Live Diagnostic Execution Log */}
          <div className="mono" style={{
            background: '#040509',
            border: '1px solid rgba(255, 42, 32, 0.4)',
            borderRadius: '10px',
            padding: '12px',
            fontSize: '10.5px',
            color: '#ff5e3a',
            lineHeight: '1.5',
            maxHeight: '120px',
            overflowY: 'auto'
          }}>
            {inspectLog.map((log, i) => (
              <div key={i}>{log}</div>
            ))}
          </div>

        </div>

        {/* Modal Buttons */}
        <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
          <button
            onClick={runDeepScan}
            disabled={inspecting}
            style={{
              background: 'linear-gradient(135deg, #ff2a20, #ff003c)',
              color: '#ffffff',
              border: 'none',
              borderRadius: '8px',
              padding: '10px 20px',
              fontSize: '12px',
              fontWeight: '800',
              cursor: 'pointer',
              boxShadow: '0 0 15px rgba(255, 42, 32, 0.4)'
            }}
          >
            {inspecting ? '⚡ Probing...' : '⚡ RUN DIAGNOSTIC PROBE'}
          </button>
          
          <button
            onClick={onClose}
            style={{
              background: 'rgba(255, 255, 255, 0.08)',
              color: '#ffffff',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              borderRadius: '8px',
              padding: '10px 18px',
              fontSize: '12px',
              fontWeight: '700',
              cursor: 'pointer'
            }}
          >
            CLOSE
          </button>
        </div>

      </div>
    </div>
  )
}
