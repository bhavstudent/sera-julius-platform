import { useEffect, useState } from 'react'
import { fetchAxiomMonitor } from '../api/client'
import GlassCard from '../components/GlassCard'
import AnimatedCounter from '../components/AnimatedCounter'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import NewsPanel from '../components/NewsPanel'

export default function AxiomMonitor() {
  const [monitorData, setMonitorData] = useState({ total_entities: 0, active_alerts: 0 })
  const [entropy, setEntropy] = useState([])
  const [alerts, setAlerts] = useState([])
  const [dismissedAlerts, setDismissedAlerts] = useState(new Set())
  const [selectedEntity, setSelectedEntity] = useState(null)

  const updateMonitor = () => {
    fetchAxiomMonitor().then(data => {
      if (data) {
        setMonitorData(data)
        setEntropy(data.entropy_summary || [])
        
        const formattedAlerts = (data.high_risk_entities || []).map(item => ({
          entity_id: item.entity_id,
          entity_name: item.entity_name || 'Unknown Entity',
          severity: (item.entropy || 0) > 2.0 ? 'CRITICAL SIREN' : 'PRE-TRANSITION',
          entropy_value: item.entropy,
          z_score: item.z_score || 2.1,
          domain: item.domain || 'technology',
          timestamp: item.timestamp || new Date().toLocaleTimeString() + ' UTC',
          description: `Shannon entropy turbulence spike detected (${item.domain || 'technology'}) — Z-score +${item.z_score || 2.1}σ`
        }))
        
        setAlerts(formattedAlerts)
        
        setSelectedEntity(prev => {
          if (!prev) return data.entropy_summary?.length > 0 ? data.entropy_summary[0] : null
          const updated = data.entropy_summary.find(item => item.entity_name === prev.entity_name)
          return updated || prev
        })
      }
    })
  }

  useEffect(() => {
    updateMonitor()
    const i = setInterval(updateMonitor, 2000)
    return () => clearInterval(i)
  }, [])

  const handleDismissAlert = (entity_name) => {
    setDismissedAlerts(prev => new Set(prev).add(entity_name))
  }

  const handleInspectAlert = (entity_name) => {
    const found = entropy.find(e => e.entity_name === entity_name)
    if (found) setSelectedEntity(found)
  }

  const activeAlertsList = alerts.filter(a => !dismissedAlerts.has(a.entity_name))

  // Get color for entropy score
  const getEntropyColor = (val) => {
    if (val > 2.2) return '#ff2a20'
    if (val > 1.4) return '#ff5e3a'
    return '#ffb340'
  }

  // Get glow style based on status
  const getStatusGlow = () => 'red'

  // Prep data for Recharts (Top 8 highest entropy)
  const chartData = [...entropy]
    .sort((a, b) => b.entropy - a.entropy)
    .slice(0, 8)
    .map(item => ({
      name: item.entity_name.split(' ')[0], // short name
      fullName: item.entity_name,
      entropy: parseFloat(item.entropy) || 0,
      status: item.status
    }))

  return (
    <div style={{ animation: 'fadeUp 0.4s ease', display: 'flex', gap: '24px', flexWrap: 'wrap', alignItems: 'stretch' }} className="axiom-monitor">
      <div style={{ flex: '3 1 350px', minWidth: '350px' }}>
      <div className="grid-2" style={{ marginBottom: 24 }}>
        <GlassCard glowType={activeAlertsList.length > 0 ? 'red' : ''}>
          <div className="stat-label">Active Pre-Transition Alerts</div>
          <div className="stat-value mono" style={{ color: activeAlertsList.length > 0 ? 'var(--red)' : 'var(--text-primary)' }}>
            <AnimatedCounter value={activeAlertsList.length} />
          </div>
          <div className="stat-sub" style={{ color: '#ff5e3a' }}>● Live Shannon Z-score spike sirens (&gt; +1.6σ)</div>
        </GlassCard>
        <GlassCard glowType="cyan">
          <div className="stat-label">Entities Monitored</div>
          <div className="stat-value mono" style={{ color: '#00f5d4' }}>
            <AnimatedCounter value={monitorData.total_entities || entropy.length} />
          </div>
          <div className="stat-sub" style={{ color: '#22c55e' }}>↑ AI autonomously discovering new entities</div>
        </GlassCard>
      </div>

      {/* Alerts Area */}
      {activeAlertsList.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          <GlassCard title={`🚨 CRITICAL PRE-TRANSITION SIRENS (${activeAlertsList.length} ACTIVE)`} glowType="red">
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {activeAlertsList.map((a, idx) => (
                <div 
                  key={`${a.entity_name}-${idx}`} 
                  style={{ 
                    padding: '14px 18px', 
                    background: a.severity.includes('CRITICAL') ? 'rgba(255, 42, 32, 0.08)' : 'rgba(255, 94, 58, 0.06)', 
                    border: `1px solid ${a.severity.includes('CRITICAL') ? 'rgba(255, 42, 32, 0.45)' : 'rgba(255, 94, 58, 0.3)'}`, 
                    borderRadius: 10,
                    display: 'flex',
                    flexWrap: 'wrap',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    gap: 12,
                    boxShadow: '0 0 15px rgba(255, 42, 32, 0.15)',
                    animation: 'fadeInSlide 0.3s ease'
                  }}
                  className="mono"
                >
                  <div style={{ flex: 1, minWidth: 200 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{ fontSize: 14 }}>🚨</span>
                      <span style={{ fontWeight: 900, color: '#ffffff', fontSize: 15 }}>{a.entity_name}</span>
                      <span style={{
                        background: 'rgba(255,42,32,0.3)',
                        color: '#ff2a20',
                        border: '1px solid rgba(255,42,32,0.6)',
                        padding: '2px 8px',
                        borderRadius: 4,
                        fontSize: 9,
                        fontWeight: 800
                      }}>
                        {a.severity}
                      </span>
                      <span style={{ fontSize: 10, color: '#ff5e3a', background: 'rgba(255,94,58,0.15)', padding: '2px 6px', borderRadius: 4 }}>
                        +{a.z_score}σ
                      </span>
                    </div>
                    <div style={{ color: '#94a3b8', fontSize: 12, marginTop: 6, display: 'flex', gap: 12, alignItems: 'center' }}>
                      <span>{a.description}</span>
                      <span style={{ fontSize: 10, color: '#64748b', marginLeft: 'auto' }}>{a.timestamp}</span>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: 9, color: '#94a3b8' }}>SHANNON ENTROPY</div>
                      <div style={{ fontSize: 20, fontWeight: 900, color: getEntropyColor(a.entropy_value) }}>
                        {a.entropy_value?.toFixed(4)}
                      </div>
                    </div>
                    
                    <div style={{ display: 'flex', gap: 6 }}>
                      <button
                        onClick={() => handleInspectAlert(a.entity_name)}
                        style={{
                          background: 'rgba(255,42,32,0.2)',
                          border: '1px solid rgba(255,42,32,0.5)',
                          color: '#ff2a20',
                          padding: '6px 10px',
                          borderRadius: 6,
                          fontSize: 10,
                          fontWeight: 800,
                          cursor: 'pointer'
                        }}
                      >
                        🎯 INSPECT
                      </button>
                      <button
                        onClick={() => handleDismissAlert(a.entity_name)}
                        style={{
                          background: 'rgba(255,255,255,0.06)',
                          border: '1px solid rgba(255,255,255,0.15)',
                          color: '#94a3b8',
                          padding: '6px 8px',
                          borderRadius: 6,
                          fontSize: 10,
                          cursor: 'pointer'
                        }}
                        title="Acknowledge & Mute Siren"
                      >
                        ✕ ACK
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </GlassCard>
        </div>
      )}

      <div className="grid-2">
        {/* Left Column: Top entropy chart & Detailed inspector */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          {/* Recharts Bar Comparison */}
          <GlassCard title="Entropy Variance - High-Risk Entities" glowType="red">
            <div style={{ minHeight: '300px', minWidth: '300px', display: 'flex', flexDirection: 'column', marginTop: 10 }}>
              {chartData.length > 0 ? (
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={9} tickLine={false} />
                    <YAxis stroke="var(--text-muted)" fontSize={9} tickLine={false} />
                    <Tooltip
                      content={({ active, payload }) => {
                        if (active && payload && payload.length) {
                          const data = payload[0].payload
                          return (
                            <div style={{ background: 'rgba(10, 15, 30, 0.95)', border: '1px solid var(--border)', padding: '10px 12px', borderRadius: 8, fontSize: 12 }}>
                              <div style={{ fontWeight: 'bold', color: 'var(--text-primary)', marginBottom: 4 }}>{data.fullName}</div>
                              <div>Entropy: <span className="mono" style={{ color: getEntropyColor(data.entropy), fontWeight: 'bold' }}>{data.entropy.toFixed(4)}</span></div>
                              <div>Status: <span style={{ textTransform: 'capitalize' }}>{data.status}</span></div>
                            </div>
                          )
                        }
                        return null
                      }}
                    />
                    <Bar dataKey="entropy" radius={[4, 4, 0, 0]}>
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={getEntropyColor(entry.entropy)} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div style={{ color: 'var(--text-muted)', fontSize: 12, textAlign: 'center', paddingTop: 80 }}>Gathering entropy registers...</div>
              )}
            </div>
          </GlassCard>

          {/* Inspector Panel */}
          {selectedEntity && (
            <GlassCard title="Entity Entropy Inspector (Real-Time Live Drift)" glowType={getStatusGlow(selectedEntity.status)}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h4 style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)' }}>{selectedEntity.entity_name}</h4>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>
                    Registry Reference Status: <span style={{ color: getEntropyColor(selectedEntity.entropy), fontWeight: 'bold', textTransform: 'capitalize' }}>{selectedEntity.status}</span>
                  </div>
                  {selectedEntity.z_score !== undefined && (
                    <div style={{ fontSize: 11, color: '#ff5e3a', marginTop: 4 }} className="mono">
                      Z-Score Anomaly: <b>{selectedEntity.z_score > 0 ? `+${selectedEntity.z_score}` : selectedEntity.z_score} σ</b> | Baseline: {selectedEntity.baseline || 0.55}
                    </div>
                  )}
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: 9, color: 'var(--text-muted)' }}>CURRENT SHANNON INDEX</div>
                  <div className="mono" style={{ fontSize: 26, fontWeight: 800, color: getEntropyColor(selectedEntity.entropy) }}>
                    {selectedEntity.entropy?.toFixed(4)}
                  </div>
                </div>
              </div>
              
              {/* Stability gauge bar indicator */}
              <div style={{ marginTop: 16 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: 'var(--text-muted)', marginBottom: 4 }}>
                  <span>STABILITY THRESHOLD</span>
                  <span>{selectedEntity.entropy > 2.2 ? 'STATE DECAY DETECTED' : 'STEADY CONFIGURATION'}</span>
                </div>
                <div style={{ width: '100%', height: 6, background: 'rgba(255,255,255,0.05)', borderRadius: 3, overflow: 'hidden' }}>
                  <div 
                    style={{ 
                      height: '100%', 
                      width: `${Math.min((selectedEntity.entropy / 4.0) * 100, 100)}%`, 
                      background: getEntropyColor(selectedEntity.entropy),
                      boxShadow: `0 0 10px ${getEntropyColor(selectedEntity.entropy)}`,
                      transition: 'width 0.4s ease'
                    }} 
                  />
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 9, color: 'var(--text-dimmed)', marginTop: 4 }} className="mono">
                  <span>0.0 (Null Signal)</span>
                  <span>2.0 (Alert Boundary)</span>
                  <span>4.0 (Turbulent Chaos)</span>
                </div>
              </div>
            </GlassCard>
          )}
        </div>

        {/* Right Column: 10x5 Dense Entropy Heatmap Grid */}
        <GlassCard title="Global Entropy Heatmap (50 resolved registry nodes)" glowType="blue">
          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 16, lineHeight: '1.4' }}>
            Hover cells to query node entropy signatures. Click to lock node target inside inspector.
          </div>
          
          {/* Heatmap Grid */}
          <div 
            style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(10, 1fr)', 
              gap: 8, 
              aspectRatio: '2/1', 
              marginBottom: 16 
            }}
          >
            {entropy.map((e, idx) => {
              const color = getEntropyColor(e.entropy)
              const isSelected = selectedEntity && selectedEntity.entity_name === e.entity_name
              
              return (
                <div
                  key={idx}
                  onClick={() => setSelectedEntity(e)}
                  style={{
                    background: color,
                    opacity: isSelected ? 1 : 0.45,
                    borderRadius: 4,
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    boxShadow: isSelected ? `0 0 12px ${color}` : 'none',
                    border: isSelected ? '1.5px solid var(--text-primary)' : '1px solid transparent'
                  }}
                  title={`${e.entity_name}: ${e.entropy?.toFixed(4)} (${e.status})`}
                />
              )}
            )}
            
            {/* Pad grid if registry incomplete */}
            {Array.from({ length: Math.max(0, 50 - entropy.length) }).map((_, idx) => (
              <div 
                key={`empty-${idx}`} 
                style={{ background: 'rgba(255,255,255,0.02)', borderRadius: 4, border: '1px dashed rgba(255,255,255,0.05)' }} 
              />
            ))}
          </div>
          
          {/* Heatmap Legend */}
          <div style={{ display: 'flex', gap: 16, fontSize: 10, color: 'var(--text-muted)', justifyContent: 'center' }} className="mono">
            <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span style={{ width: 10, height: 10, background: 'var(--cyan)', borderRadius: 2 }} /> Stable Entropy (&lt; 1.4)
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span style={{ width: 10, height: 10, background: 'var(--amber)', borderRadius: 2 }} /> Medium Entropy (1.4 - 2.2)
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span style={{ width: 10, height: 10, background: 'var(--red)', borderRadius: 2 }} /> Turbulence Spikes (&gt; 2.2)
            </span>
          </div>
        </GlassCard>
      </div>
      </div>
      <div style={{ flex: '1 1 300px', minWidth: '300px', display: 'flex', flexDirection: 'column' }}>
        <NewsPanel 
          domain={selectedEntity?.domain || 'healthcare'} 
          title={`${selectedEntity?.entity_name?.split(' ')[0] || 'System'} Telemetry News`} 
        />
      </div>
    </div>
  )
}