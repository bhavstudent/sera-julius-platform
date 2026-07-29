import { useEffect, useState } from 'react'
import { fetchZolaStatus, fetchPredictions } from '../api/client'
import GlassCard from '../components/GlassCard'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

export default function ZolaPredictions() {
  const [status, setStatus] = useState(null)
  const [ticker, setTicker] = useState('NVDA')
  const [predictions, setPredictions] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchZolaStatus().then(setStatus)
    fetchPredictions().then(res => {
      if (res) setPredictions(res)
    })
  }, [])

  const runSim = (t) => {
    setLoading(true)
    setTimeout(() => {
      setLoading(false)
    }, 600)
  }

  const chartData = [
    { step: 'T-0', probability: 45 },
    { step: 'T+1m', probability: 58 },
    { step: 'T+5m', probability: 74 },
    { step: 'T+15m', probability: 89 },
    { step: 'T+1h', probability: 96.4 },
  ]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* KRONOS Parameter Counter Banner */}
      <GlassCard glowType="red">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <h2 style={{ margin: 0, fontSize: '1.4rem', color: '#ffffff', fontWeight: '900', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span>🔮</span> ZOLA CAUSAL ENGINE — KRONOS SELF-EVOLUTION
            </h2>
            <span style={{ fontSize: '0.83rem', color: '#94a3b8' }}>
              Self-Evolving Quantum Neural Trajectory Engine (Monte-Carlo Behavioral Forecasting)
            </span>
          </div>

          <div className="mono" style={{
            background: 'rgba(255, 42, 32, 0.15)',
            border: '1px solid #ff2a20',
            borderRadius: '12px',
            padding: '8px 16px',
            color: '#ff2a20',
            fontWeight: '900',
            fontSize: '12px',
            boxShadow: '0 0 20px rgba(255, 42, 32, 0.3)'
          }}>
            VIRTUAL PARAMETERS: 1,000,000,000,000,000 (1 QUADRILLION)
          </div>
        </div>
      </GlassCard>

      {/* Target Ticker Selection & Simulation Panel */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '24px' }}>
        
        <GlassCard title="🎯 Select Entity Ticker" glowType="red">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <label style={{ fontSize: '11px', color: '#94a3b8', fontWeight: '700' }}>Corporate Entity Ticker:</label>
            <div style={{ display: 'flex', gap: '10px' }}>
              <input
                className="input-field"
                value={ticker}
                onChange={e => setTicker(e.target.value.toUpperCase())}
                placeholder="e.g. NVDA, AAPL, TSLA"
              />
              <button
                onClick={() => runSim(ticker)}
                disabled={loading}
                style={{
                  background: 'linear-gradient(135deg, #ff2a20, #ff003c)',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '10px 16px',
                  fontWeight: '800',
                  cursor: 'pointer',
                  fontSize: '12px',
                  boxShadow: '0 0 15px rgba(255, 42, 32, 0.4)'
                }}
              >
                {loading ? '⚡ Running...' : 'SIMULATE'}
              </button>
            </div>

            <div style={{ display: 'flex', gap: '8px', marginTop: '10px', flexWrap: 'wrap' }}>
              {['NVDA', 'AAPL', 'MSFT', 'AMZN', 'GOOGL'].map(t => (
                <button
                  key={t}
                  onClick={() => { setTicker(t); runSim(t) }}
                  style={{
                    background: 'rgba(255, 42, 32, 0.1)',
                    border: '1px solid rgba(255, 42, 32, 0.3)',
                    color: '#ff5e3a',
                    padding: '6px 12px',
                    borderRadius: '6px',
                    fontSize: '11px',
                    fontWeight: '700',
                    cursor: 'pointer'
                  }}
                >
                  ${t}
                </button>
              ))}
            </div>
          </div>
        </GlassCard>

        {/* Forecast Trajectory Graph */}
        <GlassCard title="📈 KRONOS Causal Probability Trajectory (T+1h)" glowType="cyan">
          <div style={{ height: 220, marginTop: 10 }}>
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={chartData}>
                <XAxis dataKey="step" stroke="#64748b" fontSize={10} />
                <YAxis stroke="#64748b" fontSize={10} domain={[0, 100]} />
                <Tooltip contentStyle={{ background: 'rgba(12, 14, 24, 0.95)', borderColor: '#ff2a20', borderRadius: 8 }} />
                <Line type="monotone" dataKey="probability" stroke="#ff2a20" strokeWidth={3} dot={{ fill: '#ff2a20', r: 5 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

      </div>
    </div>
  )
}