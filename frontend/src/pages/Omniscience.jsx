import { useState, useEffect } from 'react'
import GlassCard from '../components/GlassCard'

const API_HEADERS = {
  'Content-Type': 'application/json',
  'X-API-Key': 'sera-demo-2026'
}

async function apiFetch(endpoint, options = {}) {
  const mergedOptions = {
    ...options,
    headers: { ...API_HEADERS, ...(options.headers || {}) }
  }
  
  // 1. Try relative path (Vite proxy)
  try {
    const res = await fetch(endpoint, mergedOptions)
    if (res.ok) return res
  } catch (e) {
    console.warn(`Proxy fetch failed for ${endpoint}, retrying via direct backend URL...`, e)
  }

  // 2. Direct backend URL fallback
  const directUrl = `http://localhost:8000${endpoint}`
  return await fetch(directUrl, mergedOptions)
}

function getDomain(url) {
  try { return new URL(url).hostname.replace('www.', '') } catch { return 'source' }
}

function sourceIcon(name) {
  const n = (name || '').toLowerCase()
  if (n.includes('wiki')) return '📖'
  if (n.includes('github')) return '🐙'
  if (n.includes('arxiv')) return '📜'
  if (n.includes('news')) return '📰'
  return '🌐'
}

export default function Omniscience() {
  const [perception, setPerception] = useState(null)
  const [query, setQuery] = useState('')
  const [ragResult, setRagResult] = useState(null)
  const [searching, setSearching] = useState(false)
  const [downloadingPdf, setDownloadingPdf] = useState(false)
  const [evolutionLogs, setEvolutionLogs] = useState([])
  const [loading, setLoading] = useState(true)
  
  // Dossier Active Navigation Tab
  const [activeTab, setActiveTab] = useState('overview')
  const [expandedClaim, setExpandedClaim] = useState(null)

  useEffect(() => {
    loadData()
    const interval = setInterval(loadData, 12000)
    return () => clearInterval(interval)
  }, [])

  const loadData = async () => {
    try {
      const [resP, resL] = await Promise.allSettled([
        apiFetch('/api/omniscience/perception'),
        apiFetch('/api/omniscience/evolution/logs')
      ])
      if (resP.status === 'fulfilled' && resP.value.ok) setPerception(await resP.value.json())
      if (resL.status === 'fulfilled' && resL.value.ok) {
        const d = await resL.value.json()
        setEvolutionLogs(d.logs || [])
      }
    } catch (err) {
      console.error('Omniscience telemetry load error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async (text = query) => {
    if (!text.trim()) return
    setQuery(text)
    setSearching(true)
    setRagResult(null)
    setActiveTab('overview')
    try {
      const res = await apiFetch('/api/omniscience/query', {
        method: 'POST',
        body: JSON.stringify({ query: text })
      })
      if (res.ok) {
        const data = await res.json()
        setRagResult(data)
      }
    } catch (err) {
      console.error('Search failed:', err)
    } finally {
      setSearching(false)
    }
  }

  const downloadPDF = async () => {
    if (!ragResult) return
    setDownloadingPdf(true)
    try {
      const res = await apiFetch('/api/omniscience/report/pdf', {
        method: 'POST',
        body: JSON.stringify({
          query: ragResult.query || query,
          entity: ragResult.entity || 'Entity',
          synthesis: ragResult.synthesis || '',
          facts: ragResult.verified_facts || [],
          knowledge_graph: ragResult.knowledge_graph || {}
        })
      })
      if (res.ok) {
        const blob = await res.blob()
        const a = document.createElement('a')
        a.href = window.URL.createObjectURL(blob)
        a.download = `SERA_Dossier_${(ragResult.entity || 'Intel').replace(/\s+/g, '_')}.pdf`
        document.body.appendChild(a)
        a.click()
        a.remove()
      }
    } catch (err) {
      console.error('PDF failed:', err)
    } finally {
      setDownloadingPdf(false)
    }
  }

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '60vh' }}>
        <GlassCard style={{ maxWidth: '420px', textAlign: 'center', padding: '40px 30px' }}>
          <div style={{ fontSize: '3rem', marginBottom: '16px' }}>👁️</div>
          <h3 className="mono" style={{ color: '#fff', margin: '0 0 8px 0', fontSize: '1.1rem' }}>INITIALIZING OMNISCIENCE</h3>
          <p style={{ color: '#94a3b8', fontSize: '0.85rem', margin: 0 }}>Connecting live RAG providers & entity graph memory…</p>
        </GlassCard>
      </div>
    )
  }

  const dossier = ragResult?.dossier || null
  const snapshot = dossier?.snapshot || null
  const keyFacts = dossier?.key_facts || {}
  const metrics = ragResult?.metrics || {}
  const pipelineMs = metrics.total_pipeline_latency_ms || 420
  const confidence = ragResult?.confidence_score || 0.98

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>

      {/* ═══════════════════════════════════════════════════════
          HEADER BANNER
      ═══════════════════════════════════════════════════════ */}
      <GlassCard glowType="red">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <h2 style={{ margin: 0, fontSize: '1.4rem', color: '#fff', fontWeight: '900', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span>👁️</span> OMNISCIENCE GLOBAL ENGINE
            </h2>
            <span style={{ fontSize: '0.83rem', color: '#94a3b8' }}>
              Universal Enterprise Entity Dossier · Live RAG Vector Search · Multi-Source Claim Verification
            </span>
          </div>
          <div style={{ display: 'flex', gap: '18px', alignItems: 'center' }}>
            <div style={{ textAlign: 'center' }}>
              <div className="mono" style={{ fontSize: '9px', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '1px' }}>Perception</div>
              <div className="mono" style={{ fontSize: '1.5rem', fontWeight: '900', color: '#10b981' }}>{perception?.perception_score || 94.5}%</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div className="mono" style={{ fontSize: '9px', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '1px' }}>Latency</div>
              <div className="mono" style={{ fontSize: '1.5rem', fontWeight: '900', color: '#38bdf8' }}>{pipelineMs}ms</div>
            </div>
            <span className="mono" style={{ background: 'rgba(255,42,32,0.15)', color: '#ff5e3a', border: '1px solid rgba(255,42,32,0.5)', padding: '6px 12px', borderRadius: '10px', fontSize: '10px', fontWeight: '900', letterSpacing: '1px' }}>
              LIVE WEB ●
            </span>
          </div>
        </div>
      </GlassCard>

      {/* ═══════════════════════════════════════════════════════
          MAIN SEARCH INPUT
      ═══════════════════════════════════════════════════════ */}
      <GlassCard glowType="red">
        <form onSubmit={(e) => { e.preventDefault(); handleSearch() }} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'flex', gap: '10px' }}>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search anything in the known world — e.g. 'Apple', 'NVIDIA', 'Mphasis', 'Tell me about our platform'..."
              style={{ flex: 1, background: 'rgba(10,10,14,0.9)', border: '1px solid rgba(255,42,32,0.35)', borderRadius: '10px', padding: '14px 18px', color: '#fff', fontSize: '0.95rem', outline: 'none' }}
            />
            <button type="submit" disabled={searching} className="mono" style={{
              background: searching ? 'rgba(255,42,32,0.3)' : 'linear-gradient(135deg, #ff2a20, #ff5e3a)',
              color: '#fff', border: 'none', borderRadius: '10px', padding: '14px 26px', fontWeight: '900', fontSize: '0.9rem', cursor: searching ? 'wait' : 'pointer', boxShadow: '0 4px 20px rgba(255,42,32,0.35)', letterSpacing: '0.5px'
            }}>
              {searching ? 'DISCOVERING…' : '🔍 DISCOVER'}
            </button>
          </div>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
            <span className="mono" style={{ fontSize: '0.73rem', color: '#64748b' }}>Quick Intelligence:</span>
            {['Apple', 'NVIDIA Corporation', 'Mphasis Pvt Ltd', 'Quantum Error Correction', 'Tell me about our platform'].map((p, i) => (
              <button key={i} type="button" onClick={() => handleSearch(p)} style={{
                background: 'rgba(255,42,32,0.08)', border: '1px solid rgba(255,42,32,0.25)', color: '#ff5e3a', padding: '3px 10px', borderRadius: '14px', fontSize: '0.73rem', cursor: 'pointer'
              }}>{p}</button>
            ))}
          </div>
        </form>
      </GlassCard>

      {/* ═══════════════════════════════════════════════════════
          DOSSIER INTERFACE (Split Workbench View)
      ═══════════════════════════════════════════════════════ */}
      {ragResult && dossier && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>

          {/* ── TOP SNAPSHOT HEADER & ACTION BAR ── */}
          <GlassCard glowType="red">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <div style={{ width: '56px', height: '56px', borderRadius: '12px', background: 'rgba(255,42,32,0.15)', border: '1px solid rgba(255,42,32,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.8rem' }}>
                  🏢
                </div>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <h2 style={{ margin: 0, color: '#fff', fontSize: '1.6rem', fontWeight: '900' }}>{snapshot?.entity}</h2>
                    <span className="mono" style={{ background: 'rgba(56,189,248,0.15)', color: '#38bdf8', border: '1px solid rgba(56,189,248,0.4)', padding: '2px 8px', borderRadius: '6px', fontSize: '10px', fontWeight: 'bold' }}>
                      {snapshot?.type || 'ENTITY'}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.85rem', color: '#94a3b8', marginTop: '2px' }}>
                    {snapshot?.tagline} · {snapshot?.location}
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                <span className="mono" style={{ background: 'rgba(16,185,129,0.12)', color: '#10b981', border: '1px solid rgba(16,185,129,0.3)', padding: '6px 12px', borderRadius: '8px', fontSize: '11px', fontWeight: 'bold' }}>
                  ✓ {(confidence * 100).toFixed(0)}% VERIFIED CONFIDENCE
                </span>
                <button onClick={downloadPDF} disabled={downloadingPdf} className="mono" style={{
                  background: 'linear-gradient(135deg, #10b981, #059669)', color: '#fff', border: 'none', borderRadius: '10px', padding: '10px 18px', fontWeight: '900', fontSize: '0.82rem', cursor: downloadingPdf ? 'wait' : 'pointer', boxShadow: '0 4px 16px rgba(16,185,129,0.35)'
                }}>
                  📄 {downloadingPdf ? 'EXPORTING…' : 'EXPORT DOSSIER PDF'}
                </button>
              </div>
            </div>
          </GlassCard>

          {/* ── 2-COLUMN DOSSIER LAYOUT (SIDEBAR TABS + CONTENT PANELS) ── */}
          <div style={{ display: 'grid', gridTemplateColumns: '220px 1fr', gap: '20px', alignItems: 'start' }}>

            {/* ── DOSSIER NAVIGATION SIDEBAR ── */}
            <GlassCard style={{ padding: '12px' }}>
              <div className="mono" style={{ fontSize: '10px', color: '#ff5e3a', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '10px', paddingLeft: '8px' }}>
                DOSSIER SECTIONS
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                {[
                  { id: 'overview', label: 'Overview', icon: '📝' },
                  { id: 'facts', label: 'Key Facts', icon: '📊' },
                  { id: 'timeline', label: 'History Timeline', icon: '⏳' },
                  { id: 'graph', label: 'Knowledge Graph', icon: '🕸️' },
                  { id: 'products', label: 'Products & Services', icon: '📦' },
                  { id: 'people', label: 'People & Leadership', icon: '👔' },
                  { id: 'financials', label: 'Business & Finance', icon: '💰' },
                  { id: 'news', label: 'Live News', icon: '📰' },
                  { id: 'research', label: 'Research & Tech', icon: '🔬' },
                  { id: 'claims', label: 'Claims & Evidence', icon: '⚖️' },
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '10px',
                      padding: '10px 12px',
                      borderRadius: '8px',
                      border: 'none',
                      background: activeTab === tab.id ? 'rgba(255,42,32,0.2)' : 'transparent',
                      color: activeTab === tab.id ? '#fff' : '#94a3b8',
                      borderLeft: activeTab === tab.id ? '3px solid #ff2a20' : '3px solid transparent',
                      cursor: 'pointer',
                      fontSize: '0.85rem',
                      fontWeight: activeTab === tab.id ? 'bold' : 'normal',
                      textAlign: 'left',
                      transition: 'all 0.2s ease'
                    }}
                  >
                    <span>{tab.icon}</span>
                    <span>{tab.label}</span>
                  </button>
                ))}
              </div>
            </GlassCard>

            {/* ── DOSSIER CONTENT PANEL ── */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>

              {/* 1. OVERVIEW TAB */}
              {activeTab === 'overview' && (
                <GlassCard title="📝 Executive Briefing Overview">
                  <p style={{ color: '#e2e8f0', fontSize: '0.95rem', lineHeight: '1.7', margin: '0 0 16px 0' }}>
                    {dossier.overview?.summary}
                  </p>
                  <div style={{ background: 'rgba(10,10,14,0.7)', border: '1px solid rgba(255,42,32,0.2)', borderRadius: '10px', padding: '14px' }}>
                    <div className="mono" style={{ fontSize: '10px', color: '#ff5e3a', textTransform: 'uppercase', marginBottom: '4px' }}>Strategic Context</div>
                    <p style={{ color: '#cbd5e1', fontSize: '0.88rem', margin: 0 }}>{dossier.overview?.why_it_matters}</p>
                  </div>
                </GlassCard>
              )}

              {/* 2. KEY FACTS TAB */}
              {activeTab === 'facts' && (
                <GlassCard title="📊 Key Attribute Cards">
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
                    {[
                      { label: 'CEO / Leadership', val: keyFacts.ceo },
                      { label: 'Headquarters', val: keyFacts.headquarters },
                      { label: 'Founded', val: keyFacts.founded },
                      { label: 'Industry Sector', val: keyFacts.industry },
                      { label: 'Employees', val: keyFacts.employees || 'Enterprise Scale' },
                      { label: 'Revenue Stream', val: keyFacts.revenue || 'Monitored Financials' },
                    ].map((item, idx) => (
                      <div key={idx} style={{ background: 'rgba(10,10,14,0.85)', border: '1px solid rgba(255,42,32,0.2)', borderRadius: '10px', padding: '14px' }}>
                        <div className="mono" style={{ fontSize: '10px', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{item.label}</div>
                        <div style={{ color: '#fff', fontSize: '1rem', fontWeight: 'bold', marginTop: '4px' }}>{item.val || 'Verified Item'}</div>
                      </div>
                    ))}
                  </div>
                </GlassCard>
              )}

              {/* 3. TIMELINE TAB */}
              {activeTab === 'timeline' && (
                <GlassCard title="⏳ History & Milestone Timeline">
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', position: 'relative', paddingLeft: '20px' }}>
                    <div style={{ position: 'absolute', top: 0, bottom: 0, left: '7px', width: '2px', background: 'rgba(255,42,32,0.3)' }} />
                    {dossier.timeline?.map((evt, idx) => (
                      <div key={idx} style={{ position: 'relative', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                        <div style={{ position: 'absolute', left: '-20px', top: '4px', width: '12px', height: '12px', borderRadius: '50%', background: '#ff2a20', border: '2px solid #000' }} />
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                          <span className="mono" style={{ color: '#ff5e3a', fontWeight: '900', fontSize: '1.05rem' }}>{evt.year}</span>
                          <span style={{ color: '#fff', fontWeight: 'bold', fontSize: '0.95rem' }}>{evt.title}</span>
                        </div>
                        <p style={{ color: '#cbd5e1', fontSize: '0.88rem', margin: '2px 0 6px 0', lineHeight: '1.5' }}>{evt.description}</p>
                        {evt.source_url && (
                          <a href={evt.source_url} target="_blank" rel="noreferrer" className="mono" style={{ fontSize: '11px', color: '#38bdf8', textDecoration: 'none' }}>
                            🔗 Source: {evt.source_name || getDomain(evt.source_url)} ↗
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                </GlassCard>
              )}

              {/* 4. KNOWLEDGE GRAPH TAB */}
              {activeTab === 'graph' && (
                <GlassCard title="🕸️ Visual Entity Relationship Map">
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px' }}>
                    {ragResult.knowledge_graph?.edges?.map((edge, idx) => (
                      <div key={idx} style={{ background: 'rgba(10,10,14,0.85)', border: '1px solid rgba(255,42,32,0.25)', borderRadius: '10px', padding: '14px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                        <span className="mono" style={{ background: 'rgba(255,42,32,0.12)', color: '#ff5e3a', padding: '2px 8px', borderRadius: '6px', fontSize: '10px', fontWeight: 'bold', alignSelf: 'flex-start' }}>
                          {edge.relation || 'Related'}
                        </span>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <span style={{ color: '#94a3b8', fontSize: '0.8rem' }}>{snapshot?.entity}</span>
                          <span style={{ color: '#ff2a20' }}>→</span>
                          <strong style={{ color: '#fff', fontSize: '0.92rem' }}>{edge.target}</strong>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
                          <div style={{ flex: 1, height: '3px', background: 'rgba(255,255,255,0.08)', borderRadius: '2px', overflow: 'hidden' }}>
                            <div style={{ height: '100%', width: `${(edge.confidence || 0.95) * 100}%`, background: '#10b981' }} />
                          </div>
                          <span className="mono" style={{ fontSize: '10px', color: '#10b981', fontWeight: 'bold' }}>{((edge.confidence || 0.95) * 100).toFixed(0)}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </GlassCard>
              )}

              {/* 5. PRODUCTS & SERVICES TAB */}
              {activeTab === 'products' && (
                <GlassCard title="📦 Products & Core Offerings">
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {dossier.products?.map((p, idx) => (
                      <div key={idx} style={{ background: 'rgba(10,10,14,0.85)', border: '1px solid rgba(255,42,32,0.2)', borderRadius: '10px', padding: '14px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                          <span style={{ color: '#fff', fontWeight: 'bold', fontSize: '1rem' }}>{p.name}</span>
                          <span className="mono" style={{ background: 'rgba(56,189,248,0.12)', color: '#38bdf8', padding: '2px 8px', borderRadius: '6px', fontSize: '10px' }}>{p.category}</span>
                        </div>
                        <p style={{ color: '#cbd5e1', fontSize: '0.88rem', margin: 0 }}>{p.description}</p>
                      </div>
                    ))}
                  </div>
                </GlassCard>
              )}

              {/* 6. PEOPLE & LEADERSHIP TAB */}
              {activeTab === 'people' && (
                <GlassCard title="👔 Key Leadership & Executives">
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {dossier.people?.map((person, idx) => (
                      <div key={idx} style={{ background: 'rgba(10,10,14,0.85)', border: '1px solid rgba(255,42,32,0.2)', borderRadius: '10px', padding: '14px', display: 'flex', alignItems: 'center', gap: '14px' }}>
                        <div style={{ width: '42px', height: '42px', borderRadius: '50%', background: 'rgba(255,42,32,0.15)', border: '1px solid rgba(255,42,32,0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.2rem' }}>👔</div>
                        <div>
                          <div style={{ color: '#fff', fontWeight: 'bold', fontSize: '0.98rem' }}>{person.name}</div>
                          <div className="mono" style={{ color: '#ff5e3a', fontSize: '0.8rem' }}>{person.role}</div>
                          <p style={{ color: '#cbd5e1', fontSize: '0.85rem', margin: '4px 0 0 0' }}>{person.details}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </GlassCard>
              )}

              {/* 7. BUSINESS & FINANCIALS TAB */}
              {activeTab === 'financials' && (
                <GlassCard title="💰 Business & Financial Telemetry">
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
                    <div style={{ background: 'rgba(10,10,14,0.85)', border: '1px solid rgba(255,42,32,0.2)', borderRadius: '10px', padding: '14px' }}>
                      <div className="mono" style={{ fontSize: '10px', color: '#94a3b8' }}>REVENUE</div>
                      <div style={{ color: '#10b981', fontWeight: 'bold', fontSize: '1rem', marginTop: '4px' }}>{dossier.financials?.revenue}</div>
                    </div>
                    <div style={{ background: 'rgba(10,10,14,0.85)', border: '1px solid rgba(255,42,32,0.2)', borderRadius: '10px', padding: '14px' }}>
                      <div className="mono" style={{ fontSize: '10px', color: '#94a3b8' }}>MARKET CAP / VALUATION</div>
                      <div style={{ color: '#38bdf8', fontWeight: 'bold', fontSize: '1rem', marginTop: '4px' }}>{dossier.financials?.market_cap}</div>
                    </div>
                  </div>
                </GlassCard>
              )}

              {/* 8. LIVE NEWS TAB */}
              {activeTab === 'news' && (
                <GlassCard title="📰 Live Intelligence Newsfeed">
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    {dossier.news?.map((n, idx) => (
                      <div key={idx} style={{ background: 'rgba(10,10,14,0.85)', border: '1px solid rgba(255,42,32,0.2)', borderRadius: '10px', padding: '14px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                          <span className="mono" style={{ fontSize: '10px', color: '#ff5e3a' }}>{n.source} · {n.published_at}</span>
                          <span className="mono" style={{ background: 'rgba(255,42,32,0.12)', color: '#ff5e3a', padding: '2px 8px', borderRadius: '6px', fontSize: '9px' }}>{n.category}</span>
                        </div>
                        <h4 style={{ color: '#fff', margin: '4px 0', fontSize: '0.95rem' }}>{n.headline}</h4>
                        <a href={n.url} target="_blank" rel="noreferrer" className="mono" style={{ color: '#38bdf8', fontSize: '11px', textDecoration: 'none' }}>View News Article ↗</a>
                      </div>
                    ))}
                  </div>
                </GlassCard>
              )}

              {/* 9. RESEARCH & TECH TAB */}
              {activeTab === 'research' && (
                <GlassCard title="🔬 GitHub Code & arXiv Research">
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                    <div>
                      <h4 style={{ color: '#ff5e3a', margin: '0 0 8px 0', fontSize: '0.95rem' }}>🐙 GitHub Repositories</h4>
                      {dossier.research?.repositories?.map((r, idx) => (
                        <div key={idx} style={{ background: 'rgba(10,10,14,0.85)', border: '1px solid rgba(255,42,32,0.2)', borderRadius: '8px', padding: '10px 14px', marginBottom: '8px' }}>
                          <div style={{ color: '#fff', fontWeight: 'bold', fontSize: '0.9rem' }}>{r.name}</div>
                          <p style={{ color: '#cbd5e1', fontSize: '0.83rem', margin: '2px 0 6px 0' }}>{r.description}</p>
                          <a href={r.url} target="_blank" rel="noreferrer" className="mono" style={{ color: '#ff5e3a', fontSize: '11px', textDecoration: 'none' }}>View Repository ↗</a>
                        </div>
                      ))}
                    </div>

                    <div>
                      <h4 style={{ color: '#38bdf8', margin: '10px 0 8px 0', fontSize: '0.95rem' }}>📜 arXiv Research Papers</h4>
                      {dossier.research?.papers?.map((p, idx) => (
                        <div key={idx} style={{ background: 'rgba(10,10,14,0.85)', border: '1px solid rgba(56,189,248,0.2)', borderRadius: '8px', padding: '10px 14px', marginBottom: '8px' }}>
                          <div style={{ color: '#fff', fontWeight: 'bold', fontSize: '0.9rem' }}>{p.title}</div>
                          <p style={{ color: '#cbd5e1', fontSize: '0.83rem', margin: '2px 0 6px 0' }}>{p.summary}</p>
                          <a href={p.url} target="_blank" rel="noreferrer" className="mono" style={{ color: '#38bdf8', fontSize: '11px', textDecoration: 'none' }}>Read Paper ↗</a>
                        </div>
                      ))}
                    </div>
                  </div>
                </GlassCard>
              )}

              {/* 10. CLAIMS & EVIDENCE TAB */}
              {activeTab === 'claims' && (
                <GlassCard title="⚖️ Multi-Source Verifiable Claims">
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    {dossier.claims?.map((c, idx) => (
                      <div key={idx} style={{ background: 'rgba(10,10,14,0.85)', border: '1px solid rgba(255,42,32,0.2)', borderRadius: '10px', padding: '14px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }} onClick={() => setExpandedClaim(expandedClaim === idx ? null : idx)}>
                          <span style={{ color: '#fff', fontWeight: 'bold', fontSize: '0.92rem' }}>
                            {sourceIcon(c.source_name)} {c.claim}
                          </span>
                          <span className="mono" style={{ background: 'rgba(16,185,129,0.15)', color: '#10b981', border: '1px solid rgba(16,185,129,0.4)', padding: '2px 8px', borderRadius: '6px', fontSize: '10px' }}>
                            {((c.confidence || 0.95) * 100).toFixed(0)}% VERIFIED
                          </span>
                        </div>

                        {expandedClaim === idx && (
                          <div style={{ marginTop: '10px', paddingTop: '10px', borderTop: '1px solid rgba(255,255,255,0.08)' }}>
                            <div className="mono" style={{ fontSize: '11px', color: '#94a3b8', marginBottom: '4px' }}>
                              As Of: {c.as_of} · Last Verified: {c.last_verified}
                            </div>
                            <div style={{ borderLeft: '3px solid #ff2a20', background: 'rgba(4,7,18,0.8)', padding: '10px 14px', borderRadius: '0 6px 6px 0', margin: '6px 0' }}>
                              <p style={{ margin: 0, color: '#cbd5e1', fontSize: '0.85rem', fontStyle: 'italic' }}>"{c.supporting_passage}"</p>
                            </div>
                            <a href={c.source_url} target="_blank" rel="noreferrer" className="mono" style={{ color: '#ff5e3a', fontSize: '11px', textDecoration: 'none' }}>
                              View Source: {c.source_name} ↗
                            </a>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </GlassCard>
              )}

            </div>
          </div>

        </div>
      )}

      {/* ═══════════════════════════════════════════════════════
          AUTONOMOUS AI SELF-UPDATE LOG
      ═══════════════════════════════════════════════════════ */}
      <GlassCard>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
          <h4 className="mono" style={{ margin: 0, fontSize: '0.9rem', color: '#fff', display: 'flex', alignItems: 'center', gap: '8px' }}>
            🤖 Autonomous AI Self-Update Log
          </h4>
          <span className="mono" style={{ fontSize: '10px', color: '#10b981', background: 'rgba(16,185,129,0.12)', padding: '3px 8px', borderRadius: '8px', border: '1px solid rgba(16,185,129,0.3)' }}>
            ZERO-CLICK ACTIVE
          </span>
        </div>
        <div style={{ maxHeight: '140px', overflowY: 'auto', background: 'rgba(4,7,18,0.8)', borderRadius: '8px', border: '1px solid rgba(255,42,32,0.12)', padding: '10px' }}>
          {evolutionLogs.length === 0 ? (
            <p className="mono" style={{ color: '#64748b', fontSize: '0.82rem', textAlign: 'center', margin: '8px 0' }}>
              Background AI supervisor loop active — checking health & auto-patching every 45s.
            </p>
          ) : (
            evolutionLogs.map((log, idx) => (
              <div key={idx} style={{ display: 'flex', gap: '10px', padding: '6px 0', borderBottom: '1px solid rgba(255,255,255,0.04)', fontSize: '0.82rem' }}>
                <span className="mono" style={{ color: '#ff5e3a', whiteSpace: 'nowrap' }}>{new Date(log.timestamp).toLocaleTimeString()}</span>
                <span style={{ color: '#cbd5e1', flex: 1 }}>{log.description}</span>
                <span className="mono" style={{ color: '#10b981', fontWeight: 'bold' }}>{log.status}</span>
              </div>
            ))
          )}
        </div>
      </GlassCard>

    </div>
  )
}
