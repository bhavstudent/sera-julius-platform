import React from 'react'

const agents = [
  { name: 'ReconAgent', role: 'Asset Discovery', status: 'ACTIVE', load: 84, color: '#ff2a20', icon: '🔍', action: 'Scanning IPv4 subnet & Censys services...' },
  { name: 'AnalystAgent', role: 'Hypothesis Generator', status: 'ACTIVE', load: 92, color: '#ff5e3a', icon: '🧠', action: 'Mapping CVE vector probabilities...' },
  { name: 'ValidatorAgent', role: 'Passive Confirmation', status: 'STANDBY', load: 15, color: '#ffb340', icon: '✅', action: 'Awaiting active exploitation authorization...' },
  { name: 'Orchestrator', role: 'Autonomous Pipeline', status: 'ACTIVE', load: 78, color: '#ff2a20', icon: '⚡', action: 'Routing telemetry into KRONOS neural net...' },
  { name: 'ReportAgent', role: 'CVSS Scoring', status: 'IDLE', load: 5, color: '#8338ec', icon: '📋', action: 'Standing by for phase 5 report synthesis...' },
]

export default function AgentNeuralMatrix() {
  return (
    <div className="card glass-panel" style={{
      background: 'rgba(10, 12, 22, 0.85)',
      border: '1px solid rgba(255, 42, 32, 0.35)',
      borderRadius: '16px',
      padding: '20px',
      position: 'relative',
      overflow: 'hidden'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <div>
          <h4 style={{ margin: 0, fontSize: '1.1rem', color: '#ffffff', fontWeight: '800', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span>🤖</span> MULTI-AGENT AI NEURAL MATRIX
          </h4>
          <span style={{ fontSize: '10.5px', color: '#94a3b8' }}>Real-time 5-agent AI orchestrator load & decision pipeline</span>
        </div>
        <span className="mono" style={{ fontSize: '10px', color: '#ff2a20', background: 'rgba(255, 42, 32, 0.15)', padding: '4px 10px', borderRadius: '12px', border: '1px solid rgba(255, 42, 32, 0.3)' }}>
          LLaMA 3.1 8B • NVIDIA API
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '14px' }}>
        {agents.map((ag, i) => (
          <div key={i} style={{
            background: 'rgba(255, 42, 32, 0.05)',
            border: `1px solid ${ag.status === 'ACTIVE' ? 'rgba(255, 42, 32, 0.35)' : 'rgba(255, 255, 255, 0.08)'}`,
            borderRadius: '10px',
            padding: '14px',
            display: 'flex',
            flexDirection: 'column',
            gap: '8px',
            transition: 'all 0.2s ease'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: '800', fontSize: '0.9rem', color: '#ffffff' }}>
                <span>{ag.icon}</span>
                <span>{ag.name}</span>
              </div>
              <span style={{
                fontSize: '8.5px',
                fontWeight: 'bold',
                padding: '2px 6px',
                borderRadius: '4px',
                background: ag.status === 'ACTIVE' ? 'rgba(255, 42, 32, 0.2)' : 'rgba(255, 255, 255, 0.06)',
                color: ag.status === 'ACTIVE' ? '#ff2a20' : '#94a3b8',
                border: `1px solid ${ag.status === 'ACTIVE' ? '#ff2a20' : 'rgba(255, 255, 255, 0.15)'}`
              }}>
                {ag.status}
              </span>
            </div>

            <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
              {ag.role}
            </div>

            {/* Neural Load Bar */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '9.5px', color: '#cbd5e1', marginBottom: '3px' }}>
                <span>Neural Load</span>
                <span style={{ color: ag.color, fontWeight: 'bold' }}>{ag.load}%</span>
              </div>
              <div style={{ width: '100%', height: '5px', background: 'rgba(255,255,255,0.08)', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{ width: `${ag.load}%`, height: '100%', background: ag.color, boxShadow: `0 0 8px ${ag.color}` }} />
              </div>
            </div>

            <div style={{ fontSize: '0.73rem', color: '#ff5e3a', fontStyle: 'italic', marginTop: '2px', background: 'rgba(0,0,0,0.3)', padding: '6px', borderRadius: '4px' }}>
              ⚡ {ag.action}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

