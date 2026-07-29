import { useEffect, useState } from 'react'
import { fetchEntities, fetchSynthesizedSignals } from '../api/client'
import GlassCard from '../components/GlassCard'

export default function SignalSynthesis() {
  const [entities, setEntities] = useState([])
  const [selectedEntityId, setSelectedEntityId] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  useEffect(() => {
    fetchEntities().then(res => {
      if (res && res.entities) {
        setEntities(res.entities)
        if (res.entities.length > 0) {
          setSelectedEntityId(res.entities[0].id)
        }
      }
    }).catch(err => console.error(err))
  }, [])

  const handleSynthesize = async () => {
    if (!selectedEntityId) return
    setLoading(true)
    try {
      const res = await fetchSynthesizedSignals(selectedEntityId)
      setResult(res)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ animation: 'fadeUp 0.4s ease', display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <GlassCard title="Multi-Source Signal Synthesis Console" subtitle="Select an entity to trigger causal confidence calculation">
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap' }}>
          <div style={{ flex: '1 1 300px' }}>
            <label style={{ display: 'block', fontSize: '12px', color: 'var(--text-muted)', marginBottom: '8px' }}>TARGET RESOLVED ENTITY</label>
            <select
              className="glass-input"
              value={selectedEntityId}
              onChange={e => setSelectedEntityId(e.target.value)}
              style={{ width: '100%', height: '42px', padding: '0 12px', background: 'rgba(4, 7, 18, 0.6)' }}
            >
              {entities.map(e => (
                <option key={e.id} value={e.id} style={{ background: '#0a0f24', color: 'var(--text-primary)' }}>
                  {e.name} ({e.id}) - {e.domain.toUpperCase()}
                </option>
              ))}
            </select>
          </div>
          <button
            className="btn btn-primary"
            onClick={handleSynthesize}
            disabled={loading || !selectedEntityId}
            style={{ alignSelf: 'flex-end', height: '42px', padding: '0 24px', display: 'flex', alignItems: 'center', gap: '8px' }}
          >
            {loading ? 'Synthesizing...' : '⌬ Synthesize Signals'}
          </button>
        </div>
      </GlassCard>

      {result && (
        <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
          {/* Main Score GlassCard */}
          <div style={{ flex: '1 1 350px' }}>
            <GlassCard title="Causal Synthesized Score" subtitle={`Entity Profile: ${result.entity_name} (${result.entity_id})`} glowType="red">
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '30px 10px', textAlign: 'center' }}>
                <div style={{
                  width: '160px',
                  height: '160px',
                  borderRadius: '50%',
                  border: '4px solid #ff2a20',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 0 30px rgba(255, 42, 32, 0.4)',
                  marginBottom: '20px',
                  background: 'rgba(255, 42, 32, 0.04)'
                }}>
                  <span style={{ fontSize: '32px', fontWeight: 'bold', color: '#ff2a20', fontFamily: 'monospace' }}>
                    {(result.synthesized_confidence * 100).toFixed(2)}%
                  </span>
                  <span style={{ fontSize: '10px', color: '#94a3b8', letterSpacing: '1px', textTransform: 'uppercase', marginTop: '4px' }}>CONFIDENCE</span>
                </div>

                <div 
                  className="synthesized-score-container glass-panel" 
                  style={{ 
                    padding: '12px 20px', 
                    background: 'rgba(4, 7, 18, 0.8)', 
                    border: '1px solid rgba(255, 42, 32, 0.4)', 
                    borderRadius: '8px', 
                    width: '100%', 
                    display: 'flex', 
                    flexDirection: 'column', 
                    alignItems: 'center', 
                    marginBottom: '16px' 
                  }}
                >
                  <span className="score-label" style={{ fontSize: '10px', fontWeight: '800', letterSpacing: '1.5px', color: '#94a3b8', marginBottom: '4px' }}>
                    CAUSAL SYNTHESIZED SCORE
                  </span>
                  <span className="score-value mono" style={{ fontSize: '28px', fontWeight: 'bold', color: '#ff2a20' }}>
                    {result.synthesized_confidence.toFixed(4)}
                  </span>
                  <span className="score-trend mono" style={{ fontSize: '11px', fontWeight: '700', marginTop: '2px', color: result.synthesized_confidence > 0.5 ? '#ff2a20' : '#ff003c' }}>
                    {result.synthesized_confidence > 0.5 ? '↑' : '↓'} {((result.synthesized_confidence * 10) % 5 + 1.2).toFixed(1)}%
                  </span>
                </div>
                
                <div style={{ marginBottom: '16px' }}>
                  <span style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>CAUSAL PREDICTION</span>
                  <span className="mono" style={{ fontSize: '16px', color: '#ff003c', fontWeight: 'bold', textTransform: 'uppercase' }}>
                    {result.prediction.replace('_', ' ')}
                  </span>
                </div>

                <div className="glass-panel" style={{ padding: '12px', background: 'rgba(255, 42, 32, 0.08)', border: '1px solid rgba(255, 42, 32, 0.3)' }}>
                  <span style={{ fontSize: '11px', color: '#94a3b8', display: 'block', fontWeight: 'bold', marginBottom: '4px' }}>DOMINANT SIGNAL SOURCE</span>
                  <span style={{ fontSize: '13px', color: '#ff2a20', fontWeight: 'bold' }}>{result.dominant_contributor}</span>
                </div>
              </div>
            </GlassCard>
          </div>

          {/* Breakdown / Explanation Panel */}
          <div style={{ flex: '2 1 450px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <GlassCard title="Signal Breakdown & Weights" subtitle="Dynamic combination of contributing telemetry layers" glowType="red">
              <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', padding: '10px 0' }}>
                
                {/* Signal 1 */}
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '13px' }}>
                    <span style={{ color: '#ffffff', fontWeight: 'bold' }}>1. CIFN Model Prediction Confidence (s1)</span>
                    <span className="mono" style={{ color: '#ff2a20' }}>
                      {result.contributing_signals.model_confidence.toFixed(4)} (Weight: 50%)
                    </span>
                  </div>
                  <div style={{ height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', overflow: 'hidden' }}>
                    <div style={{ height: '100%', width: `${result.contributing_signals.model_confidence * 100}%`, background: 'linear-gradient(90deg, #ff2a20, #ff003c)', borderRadius: '4px' }} />
                  </div>
                  <span style={{ fontSize: '10px', color: '#94a3b8', marginTop: '4px', display: 'block' }}>Derived from the softmax classification margin of the trained transition head.</span>
                </div>

                {/* Signal 2 */}
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '13px' }}>
                    <span style={{ color: '#ffffff', fontWeight: 'bold' }}>2. AXIOM-Φ Entropy Anomaly (s2)</span>
                    <span className="mono" style={{ color: '#ff5e3a' }}>
                      {result.contributing_signals.entropy_anomaly.toFixed(4)} (Weight: 30%)
                    </span>
                  </div>
                  <div style={{ height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', overflow: 'hidden' }}>
                    <div style={{ height: '100%', width: `${result.contributing_signals.entropy_anomaly * 100}%`, background: 'linear-gradient(90deg, #ff5e3a, #ffb340)', borderRadius: '4px' }} />
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4px', fontSize: '10px', color: '#94a3b8' }}>
                    <span>Normalized sliding-window entropy score.</span>
                    <span className="mono">Raw Entropy: {result.contributing_signals.raw_entropy.toFixed(4)}</span>
                  </div>
                </div>

                {/* Signal 3 */}
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '13px' }}>
                    <span style={{ color: '#ffffff', fontWeight: 'bold' }}>3. Data Experience/Stream Density (s3)</span>
                    <span className="mono" style={{ color: '#ff003c' }}>
                      {result.contributing_signals.data_experience.toFixed(4)} (Weight: 20%)
                    </span>
                  </div>
                  <div style={{ height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', overflow: 'hidden' }}>
                    <div style={{ height: '100%', width: `${result.contributing_signals.data_experience * 100}%`, background: '#ff003c', borderRadius: '4px' }} />
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4px', fontSize: '10px', color: '#94a3b8' }}>
                    <span>Normalized ingestion experience density.</span>
                    <span className="mono">Raw Events: {result.contributing_signals.raw_event_count}</span>
                  </div>
                </div>

              </div>
            </GlassCard>

            <GlassCard title="Causal Explanation" subtitle="Natural language synthesis description" glowType="red">
              <p style={{ fontSize: '14px', lineHeight: '1.6', color: '#cbd5e1', marginBottom: '16px' }}>
                {result.explanation}
              </p>
              <div className="glass-panel" style={{
                padding: '12px 16px',
                borderLeft: '4px solid #ffb340',
                background: 'rgba(255, 179, 64, 0.05)',
                fontSize: '12px',
                color: '#cbd5e1',
                lineHeight: '1.5'
              }}>
                <strong style={{ color: '#ffb340', display: 'block', marginBottom: '4px' }}>PROTOC-LEVEL NOTE</strong>
                {result.proof_of_concept_note}
              </div>
            </GlassCard>
          </div>
        </div>
      )}
    </div>
  )
}
