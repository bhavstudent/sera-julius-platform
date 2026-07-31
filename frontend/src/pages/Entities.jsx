import { useEffect, useState, useCallback, useRef } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { fetchEntities } from '../api/client'
import GlassCard from '../components/GlassCard'

const API_BASE = 'https://sera-julius-intelligence-api.onrender.com'
const AUTH_HEADERS = { 'X-API-Key': 'sera-demo-2026', 'Content-Type': 'application/json' }

const DOMAIN_ICONS = {
  financial:  { icon: '💳', color: '#ff6b6b', label: 'FINANCIAL GRID' },
  healthcare: { icon: '🏥', color: '#00ff88', label: 'HEALTHCARE MESH' },
  iot:        { icon: '🔌', color: '#00d4ff', label: 'TECH MANIFOLD' },
  social:     { icon: '👥', color: '#cc5de8', label: 'SOCIAL INTEL' }
}

const mapSectorToDomain = (sector) => {
  const sec = (sector || '').toLowerCase()
  if (sec.includes('financial') || sec.includes('bank') || sec.includes('insurance')) return 'financial'
  if (sec.includes('health') || sec.includes('pharma') || sec.includes('bio') || sec.includes('medical')) return 'healthcare'
  if (sec.includes('tech') || sec.includes('software') || sec.includes('iot') || sec.includes('energy')) return 'iot'
  return 'social'
}

export default function Entities() {
  const navigate = useNavigate()
  const [entities, setEntities] = useState([])
  const [total, setTotal] = useState(0)
  const [search, setSearch] = useState('')
  const [domainFilter, setDomainFilter] = useState('all')
  const [lastRefreshed, setLastRefreshed] = useState('LIVE (3s)')
  const [liveStreamAlert, setLiveStreamAlert] = useState('🟢 STYX Real-Time Telemetry & Risk Stream Active')

  // Julius Global Search State
  const [juliusQuery, setJuliusQuery] = useState('')
  const [juliusResults, setJuliusResults] = useState([])
  const [juliusSearching, setJuliusSearching] = useState(false)
  const [juliusError, setJuliusError] = useState('')
  const debounceTimer = useRef(null)

  // Real-Time 3-Second Polling Loop
  useEffect(() => {
    const pollRealtimeEntities = async () => {
      try {
        const res = await fetchEntities()
        if (res) {
          setEntities(res.entities || [])
          setTotal(res.total || 0)
        }

        const radarRes = await fetch(`${API_BASE}/api/security/radar-targets`, {
          headers: AUTH_HEADERS
        })
        if (radarRes.ok) {
          const radarData = await radarRes.json()
          if (radarData && radarData.length > 0) {
            const target = radarData[Math.floor(Math.random() * radarData.length)]
            setLiveStreamAlert(`⚡ LIVE TELEMETRY: ${target.ip} (${target.city || 'Unknown'}) • Port ${target.ports?.[0] || 80} • ${target.severity || 'HIGH'}`)
          }
        }
        setLastRefreshed(new Date().toLocaleTimeString())
      } catch (err) {
        console.warn('[POLLER] Error:', err)
      }
    }

    pollRealtimeEntities()
    const interval = setInterval(pollRealtimeEntities, 3000)
    return () => clearInterval(interval)
  }, [])

  // Debounced Julius Search — fires 350ms after last keystroke
  const runJuliusSearch = useCallback(async (query) => {
    if (!query || query.trim().length < 1) {
      setJuliusResults([])
      setJuliusSearching(false)
      setJuliusError('')
      return
    }

    setJuliusSearching(true)
    setJuliusError('')

    try {
      const url = `${API_BASE}/api/entities/global-search?q=${encodeURIComponent(query.trim())}`
      const res = await fetch(url, { headers: AUTH_HEADERS })

      if (!res.ok) {
        setJuliusError(`Server error: ${res.status}`)
        setJuliusResults([])
        return
      }

      const data = await res.json()

      if (data && Array.isArray(data.results)) {
        setJuliusResults(data.results)
        if (data.results.length === 0) {
          setJuliusError('No results found. Try a different company name or ticker.')
        }
      } else {
        setJuliusError('Unexpected response format from server.')
        setJuliusResults([])
      }
    } catch (err) {
      console.error('[JULIUS] Search failed:', err)
      setJuliusError('Connection error. Is the backend running on port 8000?')
      setJuliusResults([])
    } finally {
      setJuliusSearching(false)
    }
  }, [])

  const handleJuliusInput = (e) => {
    const query = e.target.value
    setJuliusQuery(query)
    // Clear previous debounce
    if (debounceTimer.current) clearTimeout(debounceTimer.current)
    // Set new debounce
    debounceTimer.current = setTimeout(() => runJuliusSearch(query), 350)
  }

  const handleJuliusKeyDown = (e) => {
    if (e.key === 'Enter') {
      if (debounceTimer.current) clearTimeout(debounceTimer.current)
      runJuliusSearch(juliusQuery)
    }
  }

  const handleJuliusSubmit = (e) => {
    e.preventDefault()
    if (debounceTimer.current) clearTimeout(debounceTimer.current)
    runJuliusSearch(juliusQuery)
  }

  const filtered = entities.filter(e => {
    const mappedDomain = mapSectorToDomain(e.domain)
    const matchesSearch = (e.name || '').toLowerCase().includes(search.toLowerCase()) ||
                          (e.ticker || '').toLowerCase().includes(search.toLowerCase()) ||
                          (e.domain || '').toLowerCase().includes(search.toLowerCase())
    const matchesDomain = domainFilter === 'all' || mappedDomain === domainFilter
    return matchesSearch && matchesDomain
  })

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>

      {/* ── Top Header & Real-Time Live Telemetry Bar ── */}
      <GlassCard glowType="red">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <h2 style={{ margin: 0, fontSize: '1.4rem', color: '#ffffff', fontWeight: '900' }}>
                🏢 ENTITY REGISTRY & CYBER RISK MATRIX
              </h2>
              <span className="neon-badge-crimson mono" style={{ padding: '4px 10px', fontSize: '11px' }}>
                ● REAL-TIME MODULE ACTIVE
              </span>
            </div>
            <span style={{ fontSize: '0.83rem', color: '#94a3b8', marginTop: '4px', display: 'block' }}>
              {total} Corporate Profiles Streamed • Refreshed: {lastRefreshed}
            </span>
          </div>

          <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
            <div style={{ padding: '6px 12px', fontSize: '11px', background: 'rgba(0,255,136,0.08)', border: '1px solid rgba(0,255,136,0.35)', borderRadius: '6px', color: '#00ff88', maxWidth: '340px' }}>
              {liveStreamAlert}
            </div>
            <input
              type="text"
              placeholder="🔍 Filter loaded list..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="input-field"
              style={{ width: '220px', background: 'rgba(4, 7, 18, 0.9)', borderColor: 'rgba(255, 42, 32, 0.4)' }}
            />
          </div>
        </div>
      </GlassCard>

      {/* ── JULIUS WORLDWIDE CORPORATE SEARCH ENGINE ── */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(4,5,10,0.98) 0%, rgba(12,5,5,0.98) 100%)',
        border: '1px solid rgba(255, 42, 32, 0.5)',
        borderRadius: '14px',
        padding: '24px',
        boxShadow: '0 0 40px rgba(255, 42, 32, 0.15), inset 0 0 60px rgba(0,0,0,0.5)'
      }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '1.6rem' }}>🌐</span>
              <h3 style={{ margin: 0, fontSize: '1.25rem', color: '#ffffff', fontWeight: '900', letterSpacing: '0.5px' }}>
                JULIUS — WORLDWIDE CORPORATE SEARCH ENGINE
              </h3>
            </div>
            <p style={{ margin: '4px 0 0 34px', fontSize: '0.82rem', color: '#94a3b8' }}>
              Search any company across 190+ countries — get contact details, HQ, website, phone, sector & full SERA intel briefing
            </p>
          </div>

          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <span style={{ padding: '4px 10px', background: 'rgba(255,179,64,0.12)', border: '1px solid rgba(255,179,64,0.4)', borderRadius: '6px', fontSize: '10px', color: '#ffb340', fontWeight: '800' }}>
              GLOBAL REAL-TIME INDEX
            </span>
            <span style={{ padding: '4px 10px', background: 'rgba(0,212,255,0.08)', border: '1px solid rgba(0,212,255,0.3)', borderRadius: '6px', fontSize: '10px', color: '#00d4ff', fontWeight: '800' }}>
              ● LIVE BACKEND
            </span>
          </div>
        </div>

        {/* Search Input */}
        <form onSubmit={handleJuliusSubmit} style={{ display: 'flex', gap: '12px', marginBottom: '8px' }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <input
              type="text"
              placeholder="Search: Tesla · Siemens · Samsung · ASML · Shell · Ferrari · Reliance · Sony · Tencent · Nike · Boeing ..."
              value={juliusQuery}
              onChange={handleJuliusInput}
              onKeyDown={handleJuliusKeyDown}
              autoComplete="off"
              spellCheck="false"
              style={{
                width: '100%',
                padding: '14px 20px 14px 48px',
                fontSize: '1rem',
                background: 'rgba(4, 5, 10, 0.95)',
                border: `1px solid ${juliusSearching ? '#ffb340' : 'rgba(255, 42, 32, 0.6)'}`,
                borderRadius: '10px',
                color: '#ffffff',
                outline: 'none',
                boxShadow: '0 0 20px rgba(255, 42, 32, 0.2)',
                boxSizing: 'border-box',
                transition: 'border-color 0.2s'
              }}
            />
            <span style={{ position: 'absolute', left: '16px', top: '50%', transform: 'translateY(-50%)', fontSize: '1.1rem', pointerEvents: 'none' }}>
              {juliusSearching ? '⟳' : '🔍'}
            </span>
          </div>

          <button
            type="submit"
            style={{
              padding: '14px 28px',
              background: 'linear-gradient(135deg, #ff2a20, #ff003c)',
              color: '#ffffff',
              border: 'none',
              borderRadius: '10px',
              fontWeight: '900',
              fontSize: '0.95rem',
              cursor: 'pointer',
              whiteSpace: 'nowrap',
              boxShadow: '0 0 20px rgba(255, 42, 32, 0.5)',
              letterSpacing: '0.5px'
            }}
          >
            🔎 SEARCH
          </button>
        </form>

        {/* Quick Search Chips */}
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '18px' }}>
          {['NVIDIA', 'Tesla', 'Siemens', 'Samsung', 'Sony', 'Shell', 'ASML', 'Ferrari', 'Tencent', 'Reliance'].map(chip => (
            <button
              key={chip}
              onClick={() => {
                setJuliusQuery(chip)
                if (debounceTimer.current) clearTimeout(debounceTimer.current)
                runJuliusSearch(chip)
              }}
              style={{
                padding: '4px 12px',
                background: 'rgba(255, 42, 32, 0.1)',
                border: '1px solid rgba(255, 42, 32, 0.3)',
                borderRadius: '20px',
                color: '#94a3b8',
                fontSize: '11px',
                cursor: 'pointer',
                transition: 'all 0.2s',
                fontWeight: '600'
              }}
              onMouseEnter={e => { e.target.style.background = 'rgba(255,42,32,0.25)'; e.target.style.color = '#ffffff' }}
              onMouseLeave={e => { e.target.style.background = 'rgba(255,42,32,0.1)'; e.target.style.color = '#94a3b8' }}
            >
              {chip}
            </button>
          ))}
        </div>

        {/* Loading State */}
        {juliusSearching && (
          <div style={{ textAlign: 'center', padding: '20px', color: '#ffb340', fontSize: '0.9rem' }}>
            ⚡ Searching global corporate intelligence database...
          </div>
        )}

        {/* Error State */}
        {juliusError && !juliusSearching && (
          <div style={{ padding: '12px 16px', background: 'rgba(255,42,32,0.08)', border: '1px solid rgba(255,42,32,0.3)', borderRadius: '8px', color: '#ff6b6b', fontSize: '0.88rem' }}>
            ⚠️ {juliusError}
          </div>
        )}

        {/* Results Grid */}
        {!juliusSearching && juliusResults.length > 0 && (
          <div>
            <div style={{ fontSize: '11px', color: '#94a3b8', marginBottom: '12px' }}>
              ✅ {juliusResults.length} result{juliusResults.length !== 1 ? 's' : ''} found for "<span style={{ color: '#ffffff' }}>{juliusQuery}</span>"
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '16px' }}>
              {juliusResults.map((comp, idx) => (
                <div
                  key={comp.ticker || idx}
                  style={{
                    background: 'rgba(255,255,255,0.02)',
                    border: '1px solid rgba(255, 42, 32, 0.35)',
                    borderRadius: '10px',
                    padding: '18px',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '14px',
                    transition: 'border-color 0.2s, box-shadow 0.2s'
                  }}
                  onMouseEnter={e => { e.currentTarget.style.borderColor = '#ff2a20'; e.currentTarget.style.boxShadow = '0 0 24px rgba(255,42,32,0.2)' }}
                  onMouseLeave={e => { e.currentTarget.style.borderColor = 'rgba(255,42,32,0.35)'; e.currentTarget.style.boxShadow = 'none' }}
                >
                  {/* Company Header */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <div style={{ fontSize: '1.1rem', color: '#ffffff', fontWeight: '900', marginBottom: '2px' }}>
                        {comp.name}
                      </div>
                      <div style={{ fontSize: '0.78rem', color: '#ff2a20', fontWeight: '700' }}>
                        [{comp.ticker}] · {comp.sector}
                      </div>
                    </div>
                    <div style={{ fontSize: '0.8rem', color: '#ffb340', fontWeight: '600', textAlign: 'right', minWidth: '80px' }}>
                      {comp.country}
                    </div>
                  </div>

                  {/* Risk Score Bar */}
                  <div style={{ background: 'rgba(0,0,0,0.4)', padding: '10px 12px', borderRadius: '6px', border: '1px solid rgba(255,42,32,0.15)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: '#94a3b8', marginBottom: '5px' }}>
                      <span>CYBER STABILITY INDEX</span>
                      <span style={{ color: '#ff2a20', fontWeight: '800' }}>{((comp.risk_index || 0.88) * 100).toFixed(1)}%</span>
                    </div>
                    <div style={{ width: '100%', height: '5px', background: 'rgba(255,255,255,0.08)', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{ width: `${(comp.risk_index || 0.88) * 100}%`, height: '100%', background: 'linear-gradient(90deg, #ff2a20, #ffb340)', boxShadow: '0 0 8px rgba(255,42,32,0.6)' }} />
                    </div>
                  </div>

                  {/* Contact Details */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '5px', fontSize: '0.82rem' }}>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <span style={{ color: '#64748b', minWidth: '20px' }}>📍</span>
                      <span style={{ color: '#cbd5e1' }}>{comp.hq}</span>
                    </div>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <span style={{ color: '#64748b', minWidth: '20px' }}>🌐</span>
                      <a href={comp.website} target="_blank" rel="noreferrer" style={{ color: '#00d4ff', textDecoration: 'none', fontWeight: '600' }}>
                        {comp.website}
                      </a>
                    </div>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <span style={{ color: '#64748b', minWidth: '20px' }}>📞</span>
                      <span style={{ color: '#ffffff', fontFamily: 'monospace' }}>{comp.phone}</span>
                    </div>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <span style={{ color: '#64748b', minWidth: '20px' }}>✉️</span>
                      <span style={{ color: '#00ff88', fontFamily: 'monospace', fontSize: '0.78rem' }}>{comp.email}</span>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                    <Link
                      to={`/entity/${comp.ticker}`}
                      style={{
                        display: 'block',
                        padding: '10px',
                        background: 'linear-gradient(135deg, #ff2a20, #ff003c)',
                        color: '#ffffff',
                        borderRadius: '7px',
                        fontSize: '11px',
                        fontWeight: '800',
                        textDecoration: 'none',
                        textAlign: 'center',
                        boxShadow: '0 0 12px rgba(255,42,32,0.4)'
                      }}
                    >
                      ↗ 360° FULL BRIEFING
                    </Link>
                    <button
                      onClick={() => navigate('/causal-graph')}
                      style={{
                        padding: '10px',
                        background: 'rgba(0, 212, 255, 0.08)',
                        color: '#00d4ff',
                        border: '1px solid rgba(0, 212, 255, 0.3)',
                        borderRadius: '7px',
                        fontSize: '11px',
                        fontWeight: '800',
                        cursor: 'pointer'
                      }}
                    >
                      📐 APEX GRAPH
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* ── Sector Filter Chips ── */}
      <GlassCard glowType="amber">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ fontSize: '0.85rem', color: '#ffb340', fontWeight: '700' }}>LOCAL REGISTER DOMAIN FILTERS:</div>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {['all', 'financial', 'healthcare', 'iot', 'social'].map(d => (
              <button
                key={d}
                onClick={() => setDomainFilter(d)}
                style={{
                  background: domainFilter === d ? 'linear-gradient(135deg, #ff2a20, #ff003c)' : 'rgba(255, 42, 32, 0.08)',
                  color: domainFilter === d ? '#ffffff' : '#94a3b8',
                  border: domainFilter === d ? '1px solid #ff2a20' : '1px solid rgba(255, 42, 32, 0.25)',
                  borderRadius: '8px',
                  padding: '6px 14px',
                  fontSize: '11px',
                  fontWeight: '800',
                  cursor: 'pointer',
                  textTransform: 'uppercase',
                  boxShadow: domainFilter === d ? '0 0 12px rgba(255, 42, 32, 0.5)' : 'none'
                }}
              >
                {d === 'iot' ? 'TECH / IOT' : d}
              </button>
            ))}
          </div>
        </div>
      </GlassCard>

      {/* ── Grid of Entity Cyber Risk Cards ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(330px, 1fr))', gap: '22px' }}>
        {filtered.map(entity => {
          const domKey = mapSectorToDomain(entity.domain)
          const meta = DOMAIN_ICONS[domKey] || DOMAIN_ICONS.social
          const score = entity.expansion_score ?? 0.88
          const tickerVal = entity.ticker || entity.entity_id

          return (
            <GlassCard key={entity.entity_id || entity.ticker} glowType="red">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '14px' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '1.2rem' }}>{meta.icon}</span>
                    <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#ffffff', fontWeight: '900' }}>
                      {entity.name}
                    </h3>
                  </div>
                  <span style={{ fontSize: '0.78rem', color: '#ff2a20', fontWeight: '700', fontFamily: 'monospace' }}>
                    [{tickerVal}] · {entity.domain || 'Technology'}
                  </span>
                </div>
                <span className="neon-badge-crimson mono" style={{ fontSize: '9px' }}>
                  {meta.label}
                </span>
              </div>

              {/* Risk Score Bar */}
              <div style={{ background: 'rgba(0, 0, 0, 0.5)', padding: '10px 12px', borderRadius: '8px', border: '1px solid rgba(255, 42, 32, 0.2)', marginBottom: '14px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: '#94a3b8', marginBottom: '6px' }}>
                  <span>CYBER STABILITY INDEX</span>
                  <span style={{ color: '#ff2a20', fontWeight: '800' }}>{(score * 100).toFixed(1)}%</span>
                </div>
                <div style={{ width: '100%', height: '5px', background: 'rgba(255,255,255,0.08)', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{ width: `${score * 100}%`, height: '100%', background: 'linear-gradient(90deg, #ff2a20, #ffb340)', boxShadow: '0 0 8px rgba(255,42,32,0.7)' }} />
                </div>
              </div>

              {/* Action Buttons */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                <Link
                  to={`/entity/${tickerVal}`}
                  style={{
                    display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '8px',
                    background: 'linear-gradient(135deg, #ff2a20, #ff003c)', color: '#ffffff',
                    borderRadius: '6px', fontSize: '11px', fontWeight: '800', textDecoration: 'none',
                    boxShadow: '0 0 10px rgba(255,42,32,0.4)'
                  }}
                >
                  ↗ 360° BRIEFING
                </Link>
                <button
                  onClick={() => navigate('/causal-graph')}
                  style={{
                    display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '8px',
                    background: 'rgba(255, 42, 32, 0.08)', color: '#ff2a20',
                    border: '1px solid rgba(255, 42, 32, 0.35)', borderRadius: '6px',
                    fontSize: '11px', fontWeight: '800', cursor: 'pointer'
                  }}
                >
                  📐 GRAPH VIEW
                </button>
              </div>
            </GlassCard>
          )
        })}
      </div>
    </div>
  )
}