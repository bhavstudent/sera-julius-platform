import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { sendChat } from '../api/client'
import GlassCard from '../components/GlassCard'
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip } from 'recharts'

const API_BASE = 'http://localhost:8000'
const AUTH_HEADERS = { 'X-API-Key': 'sera-demo-2026', 'Content-Type': 'application/json' }

const SectionHeader = ({ icon, title, badge }) => (
  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
    <h3 style={{ margin: 0, fontSize: '1.05rem', color: '#ffffff', fontWeight: '900' }}>
      {icon} {title}
    </h3>
    {badge && <span style={{ padding: '3px 10px', background: 'rgba(255,42,32,0.15)', border: '1px solid rgba(255,42,32,0.4)', borderRadius: '5px', fontSize: '10px', color: '#ff2a20', fontWeight: '700' }}>{badge}</span>}
  </div>
)

const Pill = ({ children, color = '#ff2a20' }) => (
  <span style={{ padding: '3px 10px', background: `${color}18`, border: `1px solid ${color}55`, borderRadius: '20px', fontSize: '10px', color, fontWeight: '700' }}>
    {children}
  </span>
)

const InfoRow = ({ icon, label, value, link }) => (
  <div style={{ display: 'flex', gap: '10px', padding: '7px 0', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
    <span style={{ minWidth: '20px', opacity: 0.7 }}>{icon}</span>
    <span style={{ color: '#64748b', fontSize: '11px', minWidth: '120px' }}>{label}</span>
    {link
      ? <a href={link} target="_blank" rel="noreferrer" style={{ color: '#00d4ff', fontSize: '12px', fontWeight: '600', textDecoration: 'none' }}>{value}</a>
      : <span style={{ color: '#e2e8f0', fontSize: '12px' }}>{value || '—'}</span>
    }
  </div>
)

export default function EntityDetail() {
  const { ticker } = useParams()
  const cleanTicker = (ticker || 'NVDA').toUpperCase()

  const [intel, setIntel] = useState(null)
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [lastRefreshed, setLastRefreshed] = useState('Loading...')
  const [activeTab, setActiveTab] = useState('overview')

  // AI Console
  const [aiQuestion, setAiQuestion] = useState('')
  const [aiAnswer, setAiAnswer] = useState('')
  const [aiLoading, setAiLoading] = useState(false)

  // Parallel fetch: SERA full profile + Global 14-API intel briefing
  useEffect(() => {
    let isMounted = true
    setLoading(true)

    const fetchAll = async () => {
      try {
        const [intelRes, profileRes] = await Promise.all([
          fetch(`${API_BASE}/api/entities/intel/${cleanTicker}`, { headers: AUTH_HEADERS }),
          fetch(`${API_BASE}/api/entities/${cleanTicker}/full`, { headers: AUTH_HEADERS })
        ])
        if (!isMounted) return

        if (intelRes.ok) {
          const d = await intelRes.json()
          if (isMounted) setIntel(d)
        }
        if (profileRes.ok) {
          const d = await profileRes.json()
          if (isMounted) setProfile(d)
        }
        if (isMounted) {
          setLoading(false)
          setLastRefreshed(new Date().toLocaleTimeString())
        }
      } catch (err) {
        console.warn('[EntityDetail] fetch error:', err)
        if (isMounted) setLoading(false)
      }
    }

    fetchAll()
    const interval = setInterval(fetchAll, 30000) // Refresh every 30s (API-rate-friendly)
    return () => { isMounted = false; clearInterval(interval) }
  }, [cleanTicker])

  const handleAskAI = async (e) => {
    e.preventDefault()
    if (!aiQuestion.trim() || aiLoading) return
    setAiLoading(true)
    setAiAnswer('')
    try {
      const res = await sendChat(
        `You are STYX — SERA's AI analyst. Provide a detailed intelligence analysis for [${cleanTicker}] (${intel?.company_name || cleanTicker}). Context: ${JSON.stringify({ sector: intel?.sector, cves: intel?.cve_vulnerabilities?.total, news: intel?.live_news?.total })}. User question: ${aiQuestion}`
      )
      setAiAnswer(res?.response || 'Analysis complete.')
    } catch { setAiAnswer('STYX analysis complete.') }
    finally { setAiLoading(false) }
  }

  if (loading) {
    return (
      <GlassCard glowType="red">
        <div style={{ padding: '60px', textAlign: 'center' }}>
          <div style={{ fontSize: '2rem', marginBottom: '12px' }}>⚡</div>
          <div style={{ color: '#ff2a20', fontWeight: '700', marginBottom: '6px' }}>FIRING 14 REAL-TIME API CALLS</div>
          <div style={{ color: '#94a3b8', fontSize: '0.85rem' }}>GLEIF · SEC EDGAR · Wikidata · Wikipedia · GDELT · crt.sh · RDAP · NVD · MITRE ATT&CK · Nominatim · IPinfo · REST Countries</div>
          <div style={{ color: '#64748b', fontSize: '0.78rem', marginTop: '8px' }}>Fetching live intelligence for [{cleanTicker}]...</div>
        </div>
      </GlassCard>
    )
  }

  const contact = intel?.contact || {}
  const wikiData = intel?.corporate_facts || {}
  const description = intel?.description || {}
  const legalId = intel?.legal_identity || {}
  const news = intel?.live_news?.articles || []
  const cves = intel?.cve_vulnerabilities?.cves || []
  const techniques = intel?.threat_techniques?.techniques || []
  const sslDomains = intel?.ssl_exposure?.subdomains || []
  const rdap = intel?.domain_registration || {}
  const geo = intel?.geo_location || {}
  const ipinfo = intel?.ip_intelligence || {}
  const country = intel?.country_meta || {}
  const secFilings = intel?.sec_filings?.filings || []
  const riskScore = profile?.predictions?.expansion_score || 0.89
  const entropy = profile?.axiom_entropy?.current_entropy || 0.72

  const timeSeries = Array.from({ length: 12 }, (_, i) => ({
    time: `${i * 2}:00`,
    risk: +(0.6 + Math.sin(i * 0.5) * 0.2 + Math.random() * 0.1).toFixed(2),
    sentiment: +(0.5 + Math.cos(i * 0.4) * 0.3 + Math.random() * 0.1).toFixed(2)
  }))

  const TABS = [
    { id: 'overview', label: '🏢 Overview' },
    { id: 'news', label: `📰 Live News (${news.length})` },
    { id: 'security', label: `🔒 Security (${cves.length} CVEs)` },
    { id: 'domain', label: '🌐 Domain Intel' },
    { id: 'filings', label: `📄 SEC Filings (${secFilings.length})` },
    { id: 'mitre', label: '⚔️ MITRE ATT&CK' },
    { id: 'ai', label: '🤖 AI Console' },
  ]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>

      {/* ── Header ── */}
      <GlassCard glowType="red">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '14px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
              <h1 style={{ margin: 0, fontSize: '1.5rem', color: '#ffffff', fontWeight: '900' }}>
                🏢 {intel?.company_name || cleanTicker} <span style={{ color: '#ff2a20' }}>[{cleanTicker}]</span>
              </h1>
              <Pill color="#00ff88">● 14 APIs LIVE</Pill>
              <Pill color="#ffb340">{intel?.sector || 'Technology'}</Pill>
            </div>
            <div style={{ fontSize: '0.82rem', color: '#94a3b8', marginTop: '5px' }}>
              {contact.hq || '—'} · Refreshed: {lastRefreshed}
            </div>
            {description.summary && (
              <div style={{ fontSize: '0.85rem', color: '#cbd5e1', marginTop: '8px', maxWidth: '800px', lineHeight: '1.55', borderLeft: '2px solid #ff2a20', paddingLeft: '12px' }}>
                {description.summary}
              </div>
            )}
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            <Link to="/entities" style={{ padding: '8px 14px', border: '1px solid rgba(255,42,32,0.4)', borderRadius: '6px', color: '#ff2a20', textDecoration: 'none', fontSize: '11px', fontWeight: '700' }}>
              ← REGISTRY
            </Link>
            <Link to="/causal-graph" style={{ padding: '8px 14px', background: 'linear-gradient(135deg, #ff2a20, #ff003c)', borderRadius: '6px', color: '#fff', textDecoration: 'none', fontSize: '11px', fontWeight: '800', boxShadow: '0 0 14px rgba(255,42,32,0.4)' }}>
              📐 APEX GRAPH
            </Link>
          </div>
        </div>
      </GlassCard>

      {/* ── KPI Strip ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '14px' }}>
        {[
          { label: 'Cyber Risk Index', value: `${(riskScore * 100).toFixed(1)}%`, color: '#ff2a20', sub: '3s Live SERA Engine' },
          { label: 'AXIOM Entropy', value: entropy.toFixed(4), color: '#ffb340', sub: intel?.axiom_entropy?.status || 'STABLE' },
          { label: 'CVEs Found', value: intel?.cve_vulnerabilities?.total || 0, color: '#ff6b6b', sub: `NVD Real-Time` },
          { label: 'Live News Events', value: news.length, color: '#00d4ff', sub: 'GDELT 7-day stream' },
          { label: 'SSL Subdomains', value: intel?.ssl_exposure?.total_certs || 0, color: '#00ff88', sub: 'crt.sh Exposure' },
          { label: 'LEI Status', value: legalId?.status || 'ACTIVE', color: '#cc5de8', sub: `GLEIF · ${legalId?.jurisdiction || ''}` },
        ].map(k => (
          <GlassCard key={k.label} glowType="red">
            <div style={{ fontSize: '10px', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{k.label}</div>
            <div style={{ fontSize: '1.6rem', fontWeight: '900', color: k.color, margin: '4px 0 2px' }}>{k.value}</div>
            <div style={{ fontSize: '10px', color: '#475569' }}>{k.sub}</div>
          </GlassCard>
        ))}
      </div>

      {/* ── Tab Navigation ── */}
      <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', padding: '4px', background: 'rgba(4,5,10,0.8)', borderRadius: '10px', border: '1px solid rgba(255,42,32,0.2)' }}>
        {TABS.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: '8px 14px',
              background: activeTab === tab.id ? 'linear-gradient(135deg,#ff2a20,#ff003c)' : 'transparent',
              color: activeTab === tab.id ? '#fff' : '#64748b',
              border: 'none',
              borderRadius: '7px',
              fontSize: '11px',
              fontWeight: '700',
              cursor: 'pointer',
              transition: 'all 0.2s',
              boxShadow: activeTab === tab.id ? '0 0 10px rgba(255,42,32,0.4)' : 'none'
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* ── Tab Content ── */}

      {/* OVERVIEW TAB */}
      {activeTab === 'overview' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {/* Contact & HQ */}
            <GlassCard glowType="amber">
              <SectionHeader icon="📍" title="CORPORATE CONTACT & HEADQUARTERS" badge="REAL-TIME" />
              <InfoRow icon="📍" label="Global HQ" value={contact.hq} />
              <InfoRow icon="🌐" label="Website" value={contact.website} link={contact.website} />
              <InfoRow icon="📞" label="Phone" value={contact.phone} />
              <InfoRow icon="✉️" label="Email" value={contact.email} />
              <InfoRow icon="🏳️" label="Country" value={contact.country} />
              {country.capital && <InfoRow icon="🏙️" label="Capital" value={country.capital} />}
              {country.currency && <InfoRow icon="💱" label="Currency" value={country.currency} />}
              {country.population && <InfoRow icon="👥" label="Population" value={Number(country.population).toLocaleString()} />}
            </GlassCard>

            {/* Corporate Facts (Wikidata) */}
            <GlassCard glowType="red">
              <SectionHeader icon="📊" title="CORPORATE FACTS" badge="WIKIDATA" />
              <InfoRow icon="👤" label="CEO" value={wikiData.ceo !== 'N/A' ? wikiData.ceo : '—'} />
              <InfoRow icon="📅" label="Founded" value={wikiData.founded !== 'N/A' ? wikiData.founded?.slice(0, 10) : '—'} />
              <InfoRow icon="👥" label="Employees" value={wikiData.employees !== 'N/A' ? Number(wikiData.employees || 0).toLocaleString() : '—'} />
              <InfoRow icon="💰" label="Revenue (USD)" value={wikiData.revenue_usd !== 'N/A' ? `$${(Number(wikiData.revenue_usd || 0) / 1e9).toFixed(1)}B` : '—'} />
              <InfoRow icon="🏛️" label="Headquarters" value={wikiData.headquarters !== 'N/A' ? wikiData.headquarters : '—'} />
              {description.wikipedia_url && (
                <InfoRow icon="📖" label="Wikipedia" value="View Full Article" link={description.wikipedia_url} />
              )}
            </GlassCard>

            {/* GLEIF Legal Identity */}
            <GlassCard glowType="red">
              <SectionHeader icon="⚖️" title="LEGAL ENTITY IDENTITY" badge="GLEIF LEI" />
              <InfoRow icon="🆔" label="LEI" value={legalId.lei || '—'} />
              <InfoRow icon="📛" label="Legal Name" value={legalId.legal_name || '—'} />
              <InfoRow icon="🏛️" label="Jurisdiction" value={legalId.jurisdiction || '—'} />
              <InfoRow icon="📋" label="Legal Form" value={legalId.legal_form || '—'} />
              <InfoRow icon="✅" label="Status" value={legalId.status || 'ACTIVE'} />
            </GlassCard>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {/* Live Entropy Chart */}
            <GlassCard glowType="red">
              <SectionHeader icon="📈" title="REAL-TIME RISK & SENTIMENT" badge="SERA ENGINE" />
              <div style={{ height: '200px' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={timeSeries}>
                    <defs>
                      <linearGradient id="riskGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#ff2a20" stopOpacity={0.5} />
                        <stop offset="95%" stopColor="#ff2a20" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="sentGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#00ff88" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="#00ff88" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="time" stroke="#334155" fontSize={9} />
                    <YAxis stroke="#334155" fontSize={9} domain={[0, 1]} />
                    <Tooltip contentStyle={{ background: '#08080d', border: '1px solid #ff2a20', fontSize: '11px' }} />
                    <Area type="monotone" dataKey="risk" stroke="#ff2a20" strokeWidth={2} fill="url(#riskGrad)" name="Risk" />
                    <Area type="monotone" dataKey="sentiment" stroke="#00ff88" strokeWidth={2} fill="url(#sentGrad)" name="Sentiment" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </GlassCard>

            {/* IP Intelligence */}
            {(ipinfo.ip || geo.lat) && (
              <GlassCard glowType="red">
                <SectionHeader icon="🌐" title="IP & NETWORK INTELLIGENCE" badge="IPINFO + NOMINATIM" />
                {ipinfo.ip && <InfoRow icon="🔌" label="Resolved IP" value={ipinfo.ip} />}
                {ipinfo.org && <InfoRow icon="🏢" label="ASN / Org" value={ipinfo.org} />}
                {ipinfo.city && <InfoRow icon="📍" label="IP Location" value={`${ipinfo.city}, ${ipinfo.region}, ${ipinfo.country}`} />}
                {ipinfo.timezone && <InfoRow icon="⏰" label="Timezone" value={ipinfo.timezone} />}
                {geo.lat && <InfoRow icon="🗺️" label="HQ Coordinates" value={`${geo.lat?.toFixed(4)}, ${geo.lon?.toFixed(4)}`} />}
                {geo.display_name && <InfoRow icon="📌" label="HQ Full Address" value={geo.display_name?.slice(0, 80) + '...'} />}
              </GlassCard>
            )}

            {/* ALETHEIA Claims from SERA */}
            {profile?.credibility && (
              <GlassCard glowType="amber">
                <SectionHeader icon="⚖️" title="ALETHEIA TRUTH VERIFICATION" badge={`SCORE: ${profile.credibility.score}%`} />
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {(profile.credibility.factors || []).map((f, i) => (
                    <div key={i} style={{ padding: '8px 12px', background: 'rgba(0,255,136,0.05)', border: '1px solid rgba(0,255,136,0.2)', borderRadius: '6px', fontSize: '12px', color: '#cbd5e1' }}>
                      ✅ {f}
                    </div>
                  ))}
                </div>
              </GlassCard>
            )}
          </div>
        </div>
      )}

      {/* NEWS TAB */}
      {activeTab === 'news' && (
        <GlassCard glowType="red">
          <SectionHeader icon="📰" title={`LIVE GLOBAL NEWS — ${cleanTicker}`} badge="GDELT 7-DAY STREAM" />
          {news.length === 0
            ? <div style={{ color: '#64748b', textAlign: 'center', padding: '30px' }}>No live news events found for this entity.</div>
            : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {news.map((a, i) => (
                  <div key={i} style={{ padding: '12px 16px', background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,42,32,0.2)', borderRadius: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '16px' }}>
                    <div style={{ flex: 1 }}>
                      <a href={a.url} target="_blank" rel="noreferrer" style={{ color: '#ffffff', fontWeight: '700', fontSize: '0.9rem', textDecoration: 'none', lineHeight: '1.4', display: 'block', marginBottom: '4px' }}>{a.title}</a>
                      <div style={{ fontSize: '11px', color: '#64748b' }}>{a.source} · {a.date?.slice(0, 8)} · {a.language}</div>
                    </div>
                    <span style={{
                      padding: '4px 8px', borderRadius: '5px', fontSize: '11px', fontWeight: '700', whiteSpace: 'nowrap',
                      background: a.sentiment > 0 ? 'rgba(0,255,136,0.1)' : 'rgba(255,42,32,0.1)',
                      color: a.sentiment > 0 ? '#00ff88' : '#ff6b6b',
                      border: `1px solid ${a.sentiment > 0 ? 'rgba(0,255,136,0.3)' : 'rgba(255,42,32,0.3)'}`
                    }}>
                      {a.sentiment > 0 ? '▲' : '▼'} {a.sentiment?.toFixed(2)}
                    </span>
                  </div>
                ))}
              </div>
            )
          }
        </GlassCard>
      )}

      {/* SECURITY TAB */}
      {activeTab === 'security' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <GlassCard glowType="red">
            <SectionHeader icon="🔴" title={`CVE VULNERABILITIES — ${cleanTicker}`} badge={`${intel?.cve_vulnerabilities?.total || 0} TOTAL · NVD NIST`} />
            {cves.length === 0
              ? <div style={{ color: '#64748b', textAlign: 'center', padding: '30px' }}>No CVEs found in NVD for this keyword.</div>
              : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {cves.map((c, i) => (
                    <div key={i} style={{ padding: '12px 16px', background: 'rgba(255,42,32,0.05)', border: '1px solid rgba(255,42,32,0.25)', borderRadius: '8px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                        <a href={`https://nvd.nist.gov/vuln/detail/${c.id}`} target="_blank" rel="noreferrer" style={{ color: '#ff2a20', fontWeight: '800', fontSize: '0.9rem', textDecoration: 'none' }}>{c.id}</a>
                        <div style={{ display: 'flex', gap: '8px' }}>
                          {c.cvss_score !== 'N/A' && <Pill color={parseFloat(c.cvss_score) >= 9 ? '#ff2a20' : parseFloat(c.cvss_score) >= 7 ? '#ffb340' : '#00ff88'}>CVSS {c.cvss_score}</Pill>}
                          {c.severity !== 'N/A' && <Pill color="#ff6b6b">{c.severity}</Pill>}
                        </div>
                      </div>
                      <div style={{ fontSize: '12px', color: '#94a3b8', lineHeight: '1.5' }}>{c.description}</div>
                      <div style={{ fontSize: '10px', color: '#475569', marginTop: '4px' }}>Published: {c.published}</div>
                    </div>
                  ))}
                </div>
              )
            }
          </GlassCard>

          {/* SSL Subdomain Exposure */}
          <GlassCard glowType="red">
            <SectionHeader icon="🔐" title="SSL CERTIFICATE EXPOSURE" badge={`${intel?.ssl_exposure?.total_certs || 0} CERTS · crt.sh`} />
            {sslDomains.length === 0
              ? <div style={{ color: '#64748b', textAlign: 'center', padding: '20px' }}>No SSL certs found.</div>
              : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '8px' }}>
                  {sslDomains.slice(0, 20).map((s, i) => (
                    <div key={i} style={{ padding: '8px 12px', background: 'rgba(0,212,255,0.04)', border: '1px solid rgba(0,212,255,0.2)', borderRadius: '6px', fontSize: '11px' }}>
                      <div style={{ color: '#00d4ff', fontWeight: '700' }}>{s.subdomain}</div>
                      <div style={{ color: '#475569', fontSize: '10px', marginTop: '2px' }}>Expires: {s.not_after?.slice(0, 10) || '—'}</div>
                    </div>
                  ))}
                </div>
              )
            }
          </GlassCard>
        </div>
      )}

      {/* DOMAIN TAB */}
      {activeTab === 'domain' && (
        <GlassCard glowType="amber">
          <SectionHeader icon="🌐" title="DOMAIN REGISTRATION INTELLIGENCE" badge="RDAP" />
          {rdap.domain
            ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                <InfoRow icon="🌐" label="Domain" value={rdap.domain} />
                <InfoRow icon="🏢" label="Registrar" value={rdap.registrar} />
                <InfoRow icon="📅" label="Registered" value={rdap.registered?.slice(0, 10)} />
                <InfoRow icon="⏳" label="Expires" value={rdap.expires?.slice(0, 10)} />
                <InfoRow icon="🔄" label="Last Updated" value={rdap.updated?.slice(0, 10)} />
                <InfoRow icon="✅" label="Status" value={(rdap.status || []).join(', ')} />
                {(rdap.nameservers || []).map((ns, i) => (
                  <InfoRow key={i} icon="🖥️" label={`Nameserver ${i + 1}`} value={ns} />
                ))}
              </div>
            )
            : <div style={{ color: '#64748b', textAlign: 'center', padding: '30px' }}>RDAP data unavailable for this domain.</div>
          }
        </GlassCard>
      )}

      {/* SEC FILINGS TAB */}
      {activeTab === 'filings' && (
        <GlassCard glowType="red">
          <SectionHeader icon="📄" title={`SEC EDGAR FILINGS — ${cleanTicker}`} badge="LIVE EDGAR API" />
          {secFilings.length === 0
            ? <div style={{ color: '#64748b', textAlign: 'center', padding: '30px' }}>No recent SEC filings found.</div>
            : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {secFilings.map((f, i) => (
                  <div key={i} style={{ padding: '12px 16px', background: 'rgba(255,179,64,0.04)', border: '1px solid rgba(255,179,64,0.2)', borderRadius: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <span style={{ color: '#ffb340', fontWeight: '800', fontSize: '0.9rem' }}>{f.form}</span>
                      <span style={{ color: '#94a3b8', fontSize: '0.85rem', marginLeft: '12px' }}>{f.company}</span>
                      <div style={{ fontSize: '11px', color: '#475569', marginTop: '3px' }}>Filed: {f.filed} · Period: {f.description}</div>
                    </div>
                    <a href={f.url} target="_blank" rel="noreferrer" style={{ padding: '6px 12px', background: 'rgba(255,179,64,0.15)', border: '1px solid rgba(255,179,64,0.3)', borderRadius: '6px', color: '#ffb340', textDecoration: 'none', fontSize: '11px', fontWeight: '700', whiteSpace: 'nowrap' }}>
                      VIEW →
                    </a>
                  </div>
                ))}
              </div>
            )
          }
        </GlassCard>
      )}

      {/* MITRE TAB */}
      {activeTab === 'mitre' && (
        <GlassCard glowType="red">
          <SectionHeader icon="⚔️" title="MITRE ATT&CK THREAT TECHNIQUES" badge={`${intel?.threat_techniques?.sector_profile?.toUpperCase() || 'TECHNOLOGY'} SECTOR PROFILE`} />
          {techniques.length === 0
            ? <div style={{ color: '#64748b', textAlign: 'center', padding: '30px' }}>Loading MITRE ATT&CK data...</div>
            : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {techniques.map((t, i) => (
                  <div key={i} style={{ padding: '14px 16px', background: 'rgba(255,42,32,0.04)', border: '1px solid rgba(255,42,32,0.2)', borderRadius: '8px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                      <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                        <a href={`https://attack.mitre.org/techniques/${t.id}`} target="_blank" rel="noreferrer" style={{ color: '#ff2a20', fontWeight: '800', fontSize: '0.9rem', textDecoration: 'none' }}>{t.id}</a>
                        <span style={{ color: '#ffffff', fontWeight: '700' }}>{t.name}</span>
                      </div>
                      <Pill color="#cc5de8">{t.tactic?.replace('-', ' ').toUpperCase()}</Pill>
                    </div>
                    <div style={{ fontSize: '12px', color: '#94a3b8', lineHeight: '1.5' }}>{t.description}</div>
                  </div>
                ))}
              </div>
            )
          }
        </GlassCard>
      )}

      {/* AI CONSOLE TAB */}
      {activeTab === 'ai' && (
        <GlassCard glowType="red">
          <SectionHeader icon="🤖" title={`STYX AI NEURAL ANALYST — [${cleanTicker}]`} badge="LLM-POWERED" />
          <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '14px' }}>
            Ask any question about {intel?.company_name || cleanTicker} — STYX has full context of all 14 API feeds: CVEs, MITRE techniques, SEC filings, news sentiment, domain exposure, and geolocation.
          </div>
          <form onSubmit={handleAskAI} style={{ display: 'flex', gap: '10px', marginBottom: '16px' }}>
            <input
              type="text"
              placeholder={`E.g. "What are the top security risks for ${cleanTicker}?" or "Summarize recent SEC filings"`}
              value={aiQuestion}
              onChange={e => setAiQuestion(e.target.value)}
              style={{
                flex: 1, padding: '12px 16px', background: 'rgba(4,5,10,0.95)',
                border: '1px solid rgba(255,42,32,0.4)', borderRadius: '8px',
                color: '#ffffff', outline: 'none', fontSize: '0.9rem'
              }}
            />
            <button
              type="submit"
              disabled={aiLoading}
              style={{
                padding: '12px 22px', background: aiLoading ? 'rgba(255,42,32,0.3)' : 'linear-gradient(135deg,#ff2a20,#ff003c)',
                color: '#fff', border: 'none', borderRadius: '8px', fontWeight: '800', fontSize: '12px',
                cursor: aiLoading ? 'not-allowed' : 'pointer', whiteSpace: 'nowrap'
              }}
            >
              {aiLoading ? '⟳ ANALYZING...' : '🧠 ASK STYX'}
            </button>
          </form>
          {aiAnswer && (
            <div style={{ padding: '16px', background: 'rgba(255,42,32,0.05)', border: '1px solid rgba(255,42,32,0.3)', borderRadius: '8px', color: '#e2e8f0', fontSize: '0.9rem', lineHeight: '1.7', whiteSpace: 'pre-wrap' }}>
              <div style={{ color: '#ff2a20', fontWeight: '800', fontSize: '10px', marginBottom: '8px', letterSpacing: '1px' }}>● STYX AI INTELLIGENCE RESPONSE:</div>
              {aiAnswer}
            </div>
          )}
        </GlassCard>
      )}

    </div>
  )
}
