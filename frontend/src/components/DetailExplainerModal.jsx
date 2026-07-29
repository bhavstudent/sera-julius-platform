import React from 'react'

export default function DetailExplainerModal({ isOpen, onClose, data }) {
  if (!isOpen || !data) return null

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(4, 5, 10, 0.85)',
      backdropFilter: 'blur(16px)',
      WebkitBackdropFilter: 'blur(16px)',
      zIndex: 9999,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px'
    }} onClick={onClose}>
      <div style={{
        background: 'linear-gradient(135deg, rgba(12, 16, 30, 0.98) 0%, rgba(20, 26, 48, 0.95) 100%)',
        border: '1px solid rgba(255, 42, 32, 0.5)',
        borderRadius: '16px',
        width: '100%',
        maxWidth: '720px',
        maxHeight: '90vh',
        overflowY: 'auto',
        boxShadow: '0 25px 80px rgba(0, 0, 0, 0.95), 0 0 40px rgba(255, 42, 32, 0.3)',
        position: 'relative',
        padding: '28px'
      }} onClick={e => e.stopPropagation()}>
        {/* HUD Corner Reticles */}
        <div className="hud-corner top-left" />
        <div className="hud-corner top-right" />
        <div className="hud-corner bottom-left" />
        <div className="hud-corner bottom-right" />

        {/* Close Button */}
        <button onClick={onClose} style={{
          position: 'absolute',
          top: '18px',
          right: '20px',
          background: 'rgba(255, 42, 32, 0.15)',
          border: '1px solid #ff2a20',
          color: '#ffffff',
          borderRadius: '8px',
          width: '32px',
          height: '32px',
          cursor: 'pointer',
          fontWeight: 'bold',
          fontSize: '16px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>✕</button>

        {/* Header */}
        <div style={{ borderBottom: '1px solid rgba(255, 42, 32, 0.3)', paddingBottom: '14px', marginBottom: '20px' }}>
          <div style={{ fontSize: '0.75rem', color: '#ff5e3a', fontWeight: '800', textTransform: 'uppercase', letterSpacing: '1px' }}>
            CYBERSPACE SYSTEM TELEMETRY EXPLAINER
          </div>
          <div style={{ fontSize: '1.4rem', fontWeight: '900', color: '#ffffff', marginTop: '4px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span>{data.icon || '🛡️'}</span>
            <span>{data.title}</span>
          </div>
        </div>

        {/* Content Body */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '18px', fontSize: '13.5px', color: '#cbd5e1', lineHeight: '1.6' }}>
          {/* Section 1: Overview */}
          <div>
            <div style={{ fontSize: '0.8rem', fontWeight: '800', color: '#00f5d4', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '6px' }}>
              🔍 1. WHAT WE SCAN & EVALUATE
            </div>
            <p style={{ background: 'rgba(4, 5, 10, 0.6)', padding: '12px 14px', borderRadius: '8px', borderLeft: '3px solid #00f5d4' }}>
              {data.overview}
            </p>
          </div>

          {/* Section 2: Technical Mechanics */}
          {data.mechanics && (
            <div>
              <div style={{ fontSize: '0.8rem', fontWeight: '800', color: '#ffb340', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '6px' }}>
                🧠 2. UNDERLYING ALGORITHMIC MECHANICS & FORMULAS
              </div>
              <div style={{ background: 'rgba(4, 5, 10, 0.7)', padding: '12px 14px', borderRadius: '8px', borderLeft: '3px solid #ffb340', fontFamily: 'JetBrains Mono, monospace', fontSize: '12px', color: '#34d399' }}>
                {data.mechanics}
              </div>
            </div>
          )}

          {/* Section 3: Threat Impact */}
          <div>
            <div style={{ fontSize: '0.8rem', fontWeight: '800', color: '#ff2a20', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '6px' }}>
              ⚠️ 3. CYBERSECURITY IMPACT & MITRE TTP ALIGNMENT
            </div>
            <p style={{ background: 'rgba(255, 42, 32, 0.08)', padding: '12px 14px', borderRadius: '8px', borderLeft: '3px solid #ff2a20' }}>
              {data.impact}
            </p>
          </div>

          {/* Section 4: Recommended Defense */}
          {data.defense && (
            <div>
              <div style={{ fontSize: '0.8rem', fontWeight: '800', color: '#38bdf8', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '6px' }}>
                🛡️ 4. RECOMMENDED DEFENSIVE ROADMAP
              </div>
              <ul style={{ paddingLeft: '20px', background: 'rgba(56, 189, 248, 0.08)', padding: '12px 14px 12px 34px', borderRadius: '8px', borderLeft: '3px solid #38bdf8' }}>
                {data.defense.map((item, i) => (
                  <li key={i} style={{ marginBottom: '4px' }}>{item}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Footer */}
        <div style={{ marginTop: '24px', paddingTop: '14px', borderTop: '1px solid rgba(255, 42, 32, 0.2)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '11px', color: '#64748b' }}>
          <span>SERA CYBERSPACE PLATFORM ENGINE • REAL-TIME TELEMETRY</span>
          <button onClick={onClose} className="btn-primary" style={{ padding: '6px 16px', fontSize: '11px' }}>
            ACKNOWLEDGE & CLOSE
          </button>
        </div>
      </div>
    </div>
  )
}
