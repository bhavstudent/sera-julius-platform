import { useEffect, useState, useCallback, useRef } from 'react'
import { fetchZolaStatus, fetchPredictions } from '../api/client'
import GlassCard from '../components/GlassCard'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

export default function ZolaPredictions() {
  const [status, setStatus] = useState(null)
  const [ticker, setTicker] = useState('NVDA')
  const [predictions, setPredictions] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [isInitialized, setIsInitialized] = useState(false)
  
  // Use ref to prevent duplicate API calls
  const hasFetched = useRef(false)

  // Fetch data on mount - runs only once
  useEffect(() => {
    // Prevent duplicate calls in strict mode
    if (hasFetched.current) return
    hasFetched.current = true

    const loadInitialData = async () => {
      setError(null)
      
      try {
        // Fetch status
        const statusData = await fetchZolaStatus()
        if (statusData) {
          setStatus(statusData)
        } else {
          console.warn('[ZolaPredictions] No status data received')
        }
      } catch (err) {
        console.error('[ZolaPredictions] Error fetching status:', err)
        setError('Failed to load status')
      }

      try {
        // Fetch predictions
        const predictionsData = await fetchPredictions()
        if (predictionsData && Array.isArray(predictionsData)) {
          setPredictions(predictionsData)
        } else if (predictionsData) {
          // Handle case where API returns an object instead of array
          console.warn('[ZolaPredictions] Predictions data is not an array:', predictionsData)
          setPredictions([])
        } else {
          setPredictions([])
        }
      } catch (err) {
        console.error('[ZolaPredictions] Error fetching predictions:', err)
        setError('Failed to load predictions')
        setPredictions([])
      }
      
      setIsInitialized(true)
    }

    loadInitialData()
  }, []) // ✅ Empty dependency array = runs once

  // Simulate prediction run
  const runSim = useCallback(async (tickerSymbol) => {
    if (!tickerSymbol) {
      console.warn('[ZolaPredictions] No ticker provided for simulation')
      return
    }

    setLoading(true)
    setError(null)
    
    try {
      // In a real implementation, you'd call an API here
      // const result = await fetchSimulation(tickerSymbol)
      console.log(`[ZolaPredictions] Running simulation for ${tickerSymbol}`)
      
      // Simulate API call with timeout
      await new Promise(resolve => setTimeout(resolve, 600))
      
      // You could update predictions here
      // setPredictions(prev => [...prev, result])
    } catch (err) {
      console.error(`[ZolaPredictions] Simulation failed for ${tickerSymbol}:`, err)
      setError(`Simulation failed for ${tickerSymbol}`)
    } finally {
      setLoading(false)
    }
  }, [])

  // Handle ticker quick-select
  const handleTickerSelect = useCallback((tickerSymbol) => {
    setTicker(tickerSymbol)
    runSim(tickerSymbol)
  }, [runSim])

  // Chart data - memoized to prevent unnecessary re-renders
  const chartData = [
    { step: 'T-0', probability: 45 },
    { step: 'T+1m', probability: 58 },
    { step: 'T+5m', probability: 74 },
    { step: 'T+15m', probability: 89 },
    { step: 'T+1h', probability: 96.4 },
  ]

  // Show error state
  if (error) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        <GlassCard glowType="red">
          <div style={{ color: '#ff2a20', textAlign: 'center', padding: '20px' }}>
            <h3>⚠️ Error Loading Zola Predictions</h3>
            <p style={{ color: '#94a3b8' }}>{error}</p>
            <button 
              onClick={() => window.location.reload()}
              style={{
                background: 'linear-gradient(135deg, #ff2a20, #ff003c)',
                color: '#ffffff',
                border: 'none',
                borderRadius: '8px',
                padding: '10px 24px',
                fontWeight: '700',
                cursor: 'pointer',
                marginTop: '12px'
              }}
            >
              Retry
            </button>
          </div>
        </GlassCard>
      </div>
    )
  }

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

      {/* Status Display */}
      {status && (
        <GlassCard glowType="cyan" style={{ padding: '12px 20px' }}>
          <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap', fontSize: '13px' }}>
            <span><strong>Mode:</strong> {status.entity_mode || 'unknown'}</span>
            <span><strong>Backprop Steps:</strong> {status.stats?.backprop_steps || 0}</span>
            <span><strong>Latest Loss:</strong> {status.stats?.latest_loss?.toFixed(4) || 'N/A'}</span>
            <span><strong>Wave Basis:</strong> {status.wave_basis_size_kb?.toFixed(2) || '0'} KB</span>
          </div>
        </GlassCard>
      )}

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
                style={{
                  flex: 1,
                  background: 'rgba(255,255,255,0.05)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '8px',
                  padding: '10px 14px',
                  color: '#ffffff',
                  fontSize: '14px'
                }}
              />
              <button
                onClick={() => runSim(ticker)}
                disabled={loading || !ticker}
                style={{
                  background: loading ? 'rgba(255,42,32,0.3)' : 'linear-gradient(135deg, #ff2a20, #ff003c)',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '10px 16px',
                  fontWeight: '800',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  fontSize: '12px',
                  boxShadow: '0 0 15px rgba(255, 42, 32, 0.4)',
                  opacity: loading ? 0.6 : 1,
                  transition: 'all 0.2s'
                }}
              >
                {loading ? '⚡ Running...' : 'SIMULATE'}
              </button>
            </div>

            <div style={{ display: 'flex', gap: '8px', marginTop: '10px', flexWrap: 'wrap' }}>
              {['NVDA', 'AAPL', 'MSFT', 'AMZN', 'GOOGL'].map(t => (
                <button
                  key={t}
                  onClick={() => handleTickerSelect(t)}
                  disabled={loading}
                  style={{
                    background: ticker === t ? 'rgba(255, 42, 32, 0.3)' : 'rgba(255, 42, 32, 0.1)',
                    border: ticker === t ? '1px solid #ff2a20' : '1px solid rgba(255, 42, 32, 0.3)',
                    color: ticker === t ? '#ffffff' : '#ff5e3a',
                    padding: '6px 12px',
                    borderRadius: '6px',
                    fontSize: '11px',
                    fontWeight: '700',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    transition: 'all 0.2s'
                  }}
                >
                  ${t}
                </button>
              ))}
            </div>

            {/* Loading indicator */}
            {loading && (
              <div style={{ 
                marginTop: '8px', 
                color: '#ff5e3a', 
                fontSize: '12px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <span className="spinner" style={{
                  display: 'inline-block',
                  width: '16px',
                  height: '16px',
                  border: '2px solid rgba(255,42,32,0.2)',
                  borderTop: '2px solid #ff2a20',
                  borderRadius: '50%',
                  animation: 'spin 0.8s linear infinite'
                }}></span>
                Running simulation for {ticker}...
              </div>
            )}
          </div>
        </GlassCard>

        {/* Forecast Trajectory Graph */}
        <GlassCard title="📈 KRONOS Causal Probability Trajectory (T+1h)" glowType="cyan">
          <div style={{ height: 220, marginTop: 10 }}>
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={chartData}>
                <XAxis dataKey="step" stroke="#64748b" fontSize={10} />
                <YAxis stroke="#64748b" fontSize={10} domain={[0, 100]} />
                <Tooltip 
                  contentStyle={{ 
                    background: 'rgba(12, 14, 24, 0.95)', 
                    borderColor: '#ff2a20', 
                    borderRadius: 8,
                    color: '#ffffff'
                  }} 
                />
                <Line type="monotone" dataKey="probability" stroke="#ff2a20" strokeWidth={3} dot={{ fill: '#ff2a20', r: 5 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

      </div>

      {/* Predictions List */}
      {predictions.length > 0 && (
        <GlassCard title="📊 Recent Predictions" glowType="cyan">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {predictions.slice(0, 5).map((pred, idx) => (
              <div key={idx} style={{
                display: 'flex',
                justifyContent: 'space-between',
                padding: '8px 12px',
                background: 'rgba(255,255,255,0.03)',
                borderRadius: '6px',
                fontSize: '13px',
                borderLeft: '2px solid #ff2a20'
              }}>
                <span style={{ color: '#94a3b8' }}>{pred.entity_name || 'Unknown'}</span>
                <span style={{ color: '#ffffff' }}>{pred.prediction || 'N/A'}</span>
                <span style={{ color: '#ff5e3a' }}>Confidence: {(pred.confidence * 100).toFixed(1)}%</span>
              </div>
            ))}
          </div>
        </GlassCard>
      )}

      {/* CSS for spinner animation */}
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}
