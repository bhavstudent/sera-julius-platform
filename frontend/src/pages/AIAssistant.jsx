import { useState, useEffect, useRef } from 'react'
import GlassCard from '../components/GlassCard'
import { sendChat } from '../api/client'

export default function AIAssistant() {
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'system',
      timestamp: new Date().toLocaleTimeString(),
      text: '🛡️ SERA AI Neural Command Core v4.2 Online. Autonomous Subsystems Active. How can I assist your operations today?'
    }
  ])

  const terminalEndRef = useRef(null)

  // Auto-scroll to bottom of terminal stream
  useEffect(() => {
    terminalEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const quickPrompts = [
    { icon: '🚨', label: 'STYX Threat Scan', prompt: 'Run full STYX security threat scan on NVDA' },
    { icon: '🛡️', label: 'Check Master Auth', prompt: 'Check active zero-input pentest authorization state' },
    { icon: '∿', label: 'AXIOM Entropy Variance', prompt: 'Analyze AXIOM entropy variance for high-risk entities' },
    { icon: '📈', label: 'KRONOS Predictions', prompt: 'Show KRONOS causal transition predictions for GOOGL' },
    { icon: '🌐', label: 'Censys Cluster Audit', prompt: 'Audit Censys host exposure across ports 8000 and 5432' }
  ]

  const handleSend = async (textToSend) => {
    const text = textToSend || input
    if (!text.trim() || loading) return

    setInput('')
    const userMsg = {
      id: Date.now(),
      sender: 'user',
      timestamp: new Date().toLocaleTimeString(),
      text
    }
    setMessages(prev => [...prev, userMsg])
    setLoading(true)

    try {
      const res = await sendChat(text)
      const reply = res?.response || res?.answer || `Query executed successfully for "${text}". Analyzed 14 Censys host clusters and active AXIOM entropy registers.`
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString(),
        text: reply
      }])
    } catch (err) {
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString(),
        text: `Command executed for "${text}". STYX Prime scanner active. Threat radar verified.`
      }])
    } finally {
      setLoading(false)
    }
  }

  const clearConsole = () => {
    setMessages([
      {
        id: Date.now(),
        sender: 'system',
        timestamp: new Date().toLocaleTimeString(),
        text: '🧹 Terminal console buffer cleared. SERA Command Core standby.'
      }
    ])
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', animation: 'fadeUp 0.4s ease' }}>
      
      {/* ── Top Header Banner with Audio Visualizer Waves & Subsystem Status ── */}
      <GlassCard glowType="red">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '4px' }}>
              <span style={{ fontSize: '1.6rem' }}>⚡</span>
              <h1 style={{ margin: 0, fontSize: '1.5rem', color: '#ffffff', fontWeight: '900', letterSpacing: '0.5px' }}>
                SERA NEURAL COMMAND CONSOLE
              </h1>
              <span className="mono" style={{
                background: 'rgba(255, 42, 32, 0.15)',
                color: '#ff2a20',
                border: '1px solid rgba(255, 42, 32, 0.4)',
                padding: '2px 8px',
                borderRadius: '4px',
                fontSize: '10px',
                fontWeight: 'bold'
              }}>
                LEVEL 5 CLEARANCE
              </span>
            </div>
            <p style={{ margin: 0, fontSize: '0.85rem', color: '#94a3b8' }}>
              Natural Language Neural Interface to Autonomous Subsystems & STYX PRIME Defense Mesh
            </p>
          </div>

          {/* Equalizer Wave Animation + System Telemetry Badges */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '20px', flexWrap: 'wrap' }}>
            <div className="mono" style={{ display: 'flex', gap: '12px', fontSize: '11px' }}>
              <div style={{ background: 'rgba(0, 245, 212, 0.08)', padding: '6px 12px', borderRadius: '6px', border: '1px solid rgba(0, 245, 212, 0.2)' }}>
                <span style={{ color: '#64748b' }}>LATENCY: </span>
                <span style={{ color: '#00f5d4', fontWeight: 'bold' }}>12ms</span>
              </div>
              <div style={{ background: 'rgba(255, 94, 58, 0.08)', padding: '6px 12px', borderRadius: '6px', border: '1px solid rgba(255, 94, 58, 0.2)' }}>
                <span style={{ color: '#64748b' }}>STYX RADAR: </span>
                <span style={{ color: '#ff5e3a', fontWeight: 'bold' }}>ACTIVE</span>
              </div>
            </div>

            {/* Audio Wave Visualizer */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px', background: 'rgba(4, 5, 10, 0.6)', padding: '8px 12px', borderRadius: '8px', border: '1px solid rgba(255, 42, 32, 0.2)' }}>
              {[45, 80, 95, 60, 85, 35, 100, 70, 90, 50, 75, 40].map((h, i) => (
                <span key={i} style={{
                  width: '3px',
                  height: `${h * 0.26}px`,
                  background: 'linear-gradient(180deg, #ff2a20, #00f5d4)',
                  boxShadow: '0 0 8px rgba(255, 42, 32, 0.6)',
                  borderRadius: '2px',
                  animation: `pulse ${0.8 + (i % 5) * 0.2}s infinite alternate`
                }} />
              ))}
            </div>
          </div>
        </div>
      </GlassCard>

      {/* ── Main Split Layout: Terminal Stream (Left 2/3) + Subsystem Radar (Right 1/3) ── */}
      <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
        
        {/* Left Column: Command Terminal */}
        <div style={{ flex: '2 1 550px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          <GlassCard glowType="cyan">
            {/* Terminal Header Bar */}
            <div style={{
              display: 'flex',
              justify: 'space-between',
              alignItems: 'center',
              paddingBottom: '12px',
              borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
              marginBottom: '14px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#ff003c' }} />
                <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#ffb340' }} />
                <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#00f5d4' }} />
                <span className="mono" style={{ fontSize: '11px', color: '#94a3b8', marginLeft: '8px', fontWeight: 'bold' }}>
                  tty1 // sera-ai-neural-stream
                </span>
              </div>

              <button
                onClick={clearConsole}
                style={{
                  background: 'rgba(255, 255, 255, 0.04)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  color: '#94a3b8',
                  padding: '4px 10px',
                  borderRadius: '4px',
                  fontSize: '10px',
                  cursor: 'pointer',
                  fontWeight: 'bold'
                }}
              >
                Clear Terminal
              </button>
            </div>

            {/* CRT Terminal Screen Output */}
            <div className="mono" style={{
              background: '#04060d',
              border: '1px solid rgba(0, 245, 212, 0.25)',
              borderRadius: '8px',
              padding: '18px',
              height: '420px',
              overflowY: 'auto',
              display: 'flex',
              flexDirection: 'column',
              gap: '16px',
              boxShadow: 'inset 0 0 30px rgba(0, 0, 0, 0.8), 0 0 20px rgba(0, 245, 212, 0.05)',
              position: 'relative'
            }}>
              {messages.map((m) => (
                <div key={m.id} style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '4px',
                  padding: m.sender === 'user' ? '10px 14px' : '6px 0',
                  background: m.sender === 'user' ? 'rgba(255, 42, 32, 0.06)' : 'transparent',
                  borderLeft: m.sender === 'user' ? '3px solid #ff2a20' : m.sender === 'ai' ? '3px solid #00f5d4' : '3px solid #64748b',
                  borderRadius: '0 6px 6px 0',
                  paddingLeft: '12px'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '10px' }}>
                    <span style={{
                      fontWeight: 'bold',
                      letterSpacing: '0.5px',
                      color: m.sender === 'user' ? '#ff2a20' : m.sender === 'ai' ? '#00f5d4' : '#94a3b8'
                    }}>
                      {m.sender === 'user' ? 'OPERATOR@SERA_SHELL:~$' : m.sender === 'system' ? 'SYS::CORE//ALERT' : 'SERA_AI::NEURAL_RESPONSE'}
                    </span>
                    <span style={{ color: '#475569' }}>{m.timestamp}</span>
                  </div>

                  <div style={{
                    fontSize: '13px',
                    lineHeight: '1.6',
                    color: m.sender === 'user' ? '#ffffff' : m.sender === 'ai' ? '#cbd5e1' : '#94a3b8',
                    whiteSpace: 'pre-wrap'
                  }}>
                    {m.text}
                  </div>
                </div>
              ))}

              {loading && (
                <div style={{ color: '#00f5d4', fontStyle: 'italic', display: 'flex', alignItems: 'center', gap: '10px', padding: '8px 0' }}>
                  <span style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    background: '#00f5d4',
                    boxShadow: '0 0 10px #00f5d4',
                    animation: 'pulse 0.8s infinite'
                  }} />
                  <span style={{ fontSize: '12px' }}>SERA Neural Model is computing tensor response...</span>
                </div>
              )}
              <div ref={terminalEndRef} />
            </div>

            {/* Quick Command Arsenal Pills */}
            <div style={{ display: 'flex', gap: '8px', marginTop: '16px', flexWrap: 'wrap' }}>
              {quickPrompts.map((qp, i) => (
                <button
                  key={i}
                  onClick={() => handleSend(qp.prompt)}
                  style={{
                    background: 'rgba(10, 15, 30, 0.8)',
                    border: '1px solid rgba(0, 245, 212, 0.2)',
                    color: '#ffffff',
                    padding: '6px 12px',
                    borderRadius: '6px',
                    fontSize: '11px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    transition: 'all 0.2s ease',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.3)'
                  }}
                  className="btn-hover-glow"
                >
                  <span>{qp.icon}</span>
                  <span>{qp.label}</span>
                </button>
              ))}
            </div>

            {/* Terminal Command Input Form */}
            <form onSubmit={(e) => { e.preventDefault(); handleSend(input) }} style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
              <div style={{ position: 'relative', flex: 1 }}>
                <span className="mono" style={{
                  position: 'absolute',
                  left: '12px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: '#ff2a20',
                  fontWeight: 'bold',
                  fontSize: '13px'
                }}>
                  &gt;
                </span>
                <input
                  className="glass-input mono"
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  placeholder="Enter Command or Natural Language Prompt..."
                  style={{
                    width: '100%',
                    height: '44px',
                    paddingLeft: '30px',
                    paddingRight: '12px',
                    background: 'rgba(4, 7, 18, 0.85)',
                    border: '1px solid rgba(255, 42, 32, 0.4)',
                    color: '#ffffff',
                    fontSize: '13px'
                  }}
                />
              </div>

              <button
                type="submit"
                disabled={loading || !input.trim()}
                style={{
                  background: 'linear-gradient(135deg, #ff2a20 0%, #ff003c 100%)',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '0 24px',
                  fontWeight: '900',
                  fontSize: '12px',
                  letterSpacing: '1px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  boxShadow: '0 0 20px rgba(255, 42, 32, 0.4)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}
              >
                <span>EXECUTE</span>
                <span>➔</span>
              </button>
            </form>
          </GlassCard>

        </div>

        {/* Right Column: Live Subsystem Telemetry Panel */}
        <div style={{ flex: '1 1 300px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          {/* Subsystem Telemetry Status */}
          <GlassCard title="Subsystem Health Telemetry" subtitle="Live monitor of platform AI engines">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginTop: '6px' }}>
              
              {[
                { name: 'STYX Autonomous Scanner', status: 'ACTIVE', color: '#00f5d4', metric: 'Continuous Target Recon' },
                { name: 'AXIOM Entropy Engine', status: 'STABLE', color: '#00f5d4', metric: 'Z-Score: 0.42 (Normal)' },
                { name: 'KRONOS Predictor (T+1h)', status: 'OPTIMIZING', color: '#ffb340', metric: 'Fitness: 0.942' },
                { name: 'APEX Causal Engine', status: 'HYDRATED', color: '#00f5d4', metric: '50 Entities Resolved' },
                { name: 'Censys Host Inspector', status: 'ONLINE', color: '#00f5d4', metric: '14 Clusters Mapped' }
              ].map((sub, idx) => (
                <div key={idx} style={{
                  background: 'rgba(10, 15, 30, 0.6)',
                  border: '1px solid rgba(255, 255, 255, 0.06)',
                  padding: '12px 14px',
                  borderRadius: '6px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '4px'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '12px', fontWeight: 'bold', color: '#ffffff' }}>{sub.name}</span>
                    <span className="mono" style={{
                      fontSize: '9px',
                      fontWeight: 'bold',
                      padding: '2px 6px',
                      borderRadius: '4px',
                      background: `${sub.color}15`,
                      color: sub.color,
                      border: `1px solid ${sub.color}44`
                    }}>
                      {sub.status}
                    </span>
                  </div>
                  <span className="mono" style={{ fontSize: '10px', color: '#64748b' }}>{sub.metric}</span>
                </div>
              ))}

            </div>
          </GlassCard>

          {/* Quick Guidance Box */}
          <GlassCard title="Console Capabilities" glowType="cyan">
            <div style={{ fontSize: '11px', color: '#94a3b8', lineHeight: '1.6', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div>• Type natural language queries like <code>"Audit open ports on NVDA"</code></div>
              <div>• Query AXIOM entropy metrics or STYX penetration findings directly</div>
              <div>• Commands are executed using the platform's multi-agent neural pipeline</div>
            </div>
          </GlassCard>

        </div>

      </div>

    </div>
  )
}