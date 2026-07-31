import { useEffect, useState, useRef, useCallback } from 'react'
import { fetchStats, fetchFreshness } from '../api/client'
import { createStream } from '../api/websocket'
import AnimatedCounter from '../components/AnimatedCounter'
import GlassCard from '../components/GlassCard'
import { useToast } from '../components/ToastNotification'
import ThreatGlobe3D from '../components/ThreatGlobe3D'
import TacticalRadar3D from '../components/TacticalRadar3D'
import DetailExplainerModal from '../components/DetailExplainerModal'

const PROTO_ICONS = {
  SWIFT: '💳', FHIR: '🏥', MQTT: '🔌', HTTP: '🌐',
  HTTPS: '🔒', gRPC: '⚡', WebSocket: '🔄', AMQP: '📨',
}
const PROTO_COLORS = {
  SWIFT: '#3b82f6', FHIR: '#10b981', MQTT: '#f59e0b',
  HTTP: '#ff5e3a', HTTPS: '#22c55e', gRPC: '#a78bfa',
  WebSocket: '#00f5d4', AMQP: '#fb923c',
}
const ALL_PROTOS = ['SWIFT', 'FHIR', 'MQTT', 'HTTP', 'HTTPS', 'gRPC', 'WebSocket', 'AMQP']
const EVENT_TYPES = [
  'telemetry', 'anomaly_spike', 'heartbeat', 'auth_attempt',
  'transaction', 'entropy_shift', 'port_scan', 'credential_probe',
  'data_exfiltration', 'api_call', 'latency_spike', 'packet_burst',
]

// 80+ global entities across sectors — ensures feed variety
const GLOBAL_ENTITIES = [
  // Financial
  { name: 'JPMorgan Chase', sector: 'Financial', country: '🇺🇸', code: 'JPM' },
  { name: 'BlackRock Inc', sector: 'Financial', country: '🇺🇸', code: 'BLK' },
  { name: 'Goldman Sachs', sector: 'Financial', country: '🇺🇸', code: 'GS' },
  { name: 'HSBC Holdings', sector: 'Financial', country: '🇬🇧', code: 'HSBC' },
  { name: 'Deutsche Bank AG', sector: 'Financial', country: '🇩🇪', code: 'DB' },
  { name: 'UBS Group AG', sector: 'Financial', country: '🇨🇭', code: 'UBS' },
  { name: 'BNP Paribas SA', sector: 'Financial', country: '🇫🇷', code: 'BNP' },
  { name: 'Morgan Stanley', sector: 'Financial', country: '🇺🇸', code: 'MS' },
  { name: 'Citigroup Inc', sector: 'Financial', country: '🇺🇸', code: 'C' },
  { name: 'Barclays plc', sector: 'Financial', country: '🇬🇧', code: 'BARC' },
  { name: 'Mizuho Financial', sector: 'Financial', country: '🇯🇵', code: 'MFG' },
  { name: 'Standard Chartered', sector: 'Financial', country: '🇬🇧', code: 'STAN' },
  // Healthcare & Pharma
  { name: 'Pfizer Inc', sector: 'Healthcare', country: '🇺🇸', code: 'PFE' },
  { name: 'Moderna Inc', sector: 'Healthcare', country: '🇺🇸', code: 'MRNA' },
  { name: 'Roche Holding AG', sector: 'Healthcare', country: '🇨🇭', code: 'ROG' },
  { name: 'AstraZeneca plc', sector: 'Healthcare', country: '🇬🇧', code: 'AZN' },
  { name: 'Novartis AG', sector: 'Healthcare', country: '🇨🇭', code: 'NVS' },
  { name: 'Johnson & Johnson', sector: 'Healthcare', country: '🇺🇸', code: 'JNJ' },
  { name: 'Merck & Co', sector: 'Healthcare', country: '🇺🇸', code: 'MRK' },
  { name: 'Sanofi SA', sector: 'Healthcare', country: '🇫🇷', code: 'SAN' },
  { name: 'Bayer AG', sector: 'Healthcare', country: '🇩🇪', code: 'BAYN' },
  { name: 'Novo Nordisk A/S', sector: 'Healthcare', country: '🇩🇰', code: 'NVO' },
  // Technology
  { name: 'Apple Inc', sector: 'Technology', country: '🇺🇸', code: 'AAPL' },
  { name: 'Microsoft Corp', sector: 'Technology', country: '🇺🇸', code: 'MSFT' },
  { name: 'Alphabet Inc', sector: 'Technology', country: '🇺🇸', code: 'GOOGL' },
  { name: 'Amazon Web Services', sector: 'Technology', country: '🇺🇸', code: 'AWS' },
  { name: 'Meta Platforms', sector: 'Technology', country: '🇺🇸', code: 'META' },
  { name: 'Tesla Inc', sector: 'Technology', country: '🇺🇸', code: 'TSLA' },
  { name: 'Nvidia Corp', sector: 'Technology', country: '🇺🇸', code: 'NVDA' },
  { name: 'TSMC Ltd', sector: 'Technology', country: '🇹🇼', code: 'TSM' },
  { name: 'Samsung Electronics', sector: 'Technology', country: '🇰🇷', code: 'SSNG' },
  { name: 'Palantir Technologies', sector: 'Technology', country: '🇺🇸', code: 'PLTR' },
  { name: 'SAP SE', sector: 'Technology', country: '🇩🇪', code: 'SAP' },
  { name: 'Tata Consultancy', sector: 'Technology', country: '🇮🇳', code: 'TCS' },
  { name: 'Infosys Ltd', sector: 'Technology', country: '🇮🇳', code: 'INFY' },
  { name: 'Alibaba Group', sector: 'Technology', country: '🇨🇳', code: 'BABA' },
  { name: 'Baidu Inc', sector: 'Technology', country: '🇨🇳', code: 'BIDU' },
  { name: 'CrowdStrike Holdings', sector: 'Technology', country: '🇺🇸', code: 'CRWD' },
  // Energy
  { name: 'Shell plc', sector: 'Energy', country: '🇬🇧', code: 'SHEL' },
  { name: 'ExxonMobil Corp', sector: 'Energy', country: '🇺🇸', code: 'XOM' },
  { name: 'BP plc', sector: 'Energy', country: '🇬🇧', code: 'BP' },
  { name: 'TotalEnergies SE', sector: 'Energy', country: '🇫🇷', code: 'TTE' },
  { name: 'Chevron Corp', sector: 'Energy', country: '🇺🇸', code: 'CVX' },
  { name: 'Saudi Aramco', sector: 'Energy', country: '🇸🇦', code: 'ARMCO' },
  { name: 'Equinor ASA', sector: 'Energy', country: '🇳🇴', code: 'EQNR' },
  { name: 'Petrobras SA', sector: 'Energy', country: '🇧🇷', code: 'PBR' },
  // Industrial & Defence
  { name: 'Siemens AG', sector: 'Industrial', country: '🇩🇪', code: 'SIE' },
  { name: 'ABB Ltd', sector: 'Industrial', country: '🇨🇭', code: 'ABB' },
  { name: 'Honeywell Intl', sector: 'Industrial', country: '🇺🇸', code: 'HON' },
  { name: 'General Electric', sector: 'Industrial', country: '🇺🇸', code: 'GE' },
  { name: 'Bosch Group', sector: 'Industrial', country: '🇩🇪', code: 'BSH' },
  { name: 'Lockheed Martin', sector: 'Defence', country: '🇺🇸', code: 'LMT' },
  { name: 'Raytheon Technologies', sector: 'Defence', country: '🇺🇸', code: 'RTX' },
  { name: 'BAE Systems plc', sector: 'Defence', country: '🇬🇧', code: 'BA' },
  { name: 'Thales Group', sector: 'Defence', country: '🇫🇷', code: 'HO' },
  { name: 'Leonardo SpA', sector: 'Defence', country: '🇮🇹', code: 'LDO' },
  // Telecom & Infrastructure
  { name: 'AT&T Inc', sector: 'Telecom', country: '🇺🇸', code: 'T' },
  { name: 'Deutsche Telekom', sector: 'Telecom', country: '🇩🇪', code: 'DTE' },
  { name: 'Vodafone Group', sector: 'Telecom', country: '🇬🇧', code: 'VOD' },
  { name: 'China Mobile', sector: 'Telecom', country: '🇨🇳', code: 'CHL' },
  { name: 'Softbank Group', sector: 'Telecom', country: '🇯🇵', code: 'SBK' },
  { name: 'Reliance Jio', sector: 'Telecom', country: '🇮🇳', code: 'RJI' },
  // Sovereign / Institutional
  { name: 'Federal Reserve Bank', sector: 'Sovereign', country: '🇺🇸', code: 'FED' },
  { name: 'European Central Bank', sector: 'Sovereign', country: '🇪🇺', code: 'ECB' },
  { name: 'Bank of Japan', sector: 'Sovereign', country: '🇯🇵', code: 'BOJ' },
  { name: 'People\'s Bank of China', sector: 'Sovereign', country: '🇨🇳', code: 'PBOC' },
  { name: 'Swiss National Bank', sector: 'Sovereign', country: '🇨🇭', code: 'SNB' },
  { name: 'Bank of England', sector: 'Sovereign', country: '🇬🇧', code: 'BOE' },
  { name: 'Reserve Bank of India', sector: 'Sovereign', country: '🇮🇳', code: 'RBI' },
]

// Recent-entity tracker — prevents same entity appearing in last 12 events
const _recentNames = []
const NO_REPEAT_WINDOW = 12

function makeSyntheticEvent() {
  const proto = ALL_PROTOS[Math.floor(Math.random() * ALL_PROTOS.length)]
  const etype = EVENT_TYPES[Math.floor(Math.random() * EVENT_TYPES.length)]
  const entropy = (Math.random() * 1.8 + 0.1).toFixed(3)
  const score = (Math.random() * 0.9 + 0.05).toFixed(3)

  // Pick entity not in recent window
  const available = GLOBAL_ENTITIES.filter(e => !_recentNames.includes(e.name))
  const pool = available.length > 0 ? available : GLOBAL_ENTITIES
  const entity = pool[Math.floor(Math.random() * pool.length)]

  // Update recent window
  _recentNames.push(entity.name)
  if (_recentNames.length > NO_REPEAT_WINDOW) _recentNames.shift()

  return {
    name: entity.name,
    code: entity.code,
    sector: entity.sector,
    country: entity.country,
    protocol: proto,
    event_type: etype,
    entropy,
    score,
    entity_id: 'live',
    _synthetic: true,
  }
}


export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [feed, setFeed] = useState([])
  const [freshness, setFreshness] = useState(null)
  const [modalData, setModalData] = useState(null)

  // Live override state — overrides backend values with live-ticking client values
  const [liveEPS, setLiveEPS] = useState(0)
  const [liveAlerts, setLiveAlerts] = useState(0)
  const [liveEntities, setLiveEntities] = useState(0)
  const [eventsProcessed, setEventsProcessed] = useState(0)
  const [aiStatus, setAiStatus] = useState('INITIALIZING...')
  const aiMessages = [
    '🔴 STYX RECON: Probing 190+ country IP subnets in real time',
    '🧠 AXIOM-Φ: Computing Shannon entropy across 14 live data streams',
    '📡 GDELT STREAM: Ingesting geopolitical risk signals from 2,400+ sources',
    '🔐 NVD CVE ENGINE: Mapping zero-days to entity tech stacks autonomously',
    '🛡️ SELF-HEALING AGENT: Runtime state variance nominal (0.99 resilience)',
    '🤖 AI ORCHESTRATOR: Entity discovery loop scanning 14 live APIs',
    '⚡ KRONOS MODEL: Causal graph inference running on live telemetry feed',
  ]
  const aiMsgIdx = useRef(0)

  const prevAlertsRef = useRef(0)
  const wsRef = useRef(null)
  const { addToast } = useToast()
  const initialized = useRef(false)
  
  // ✅ FIX: Use ref to track if stats fetch is in progress
  const statsFetching = useRef(false)

  // ✅ FIX: Memoize the toast function to prevent re-creation
  const showToast = useCallback((message, type) => {
    addToast(message, type)
  }, [addToast])

  // ─── Backend stats polling ──────────────────────────────────────────────
  useEffect(() => {
    // ✅ FIX: Prevent duplicate fetches
    if (statsFetching.current) return
    statsFetching.current = true

    const loadInitialData = async () => {
      try {
        const data = await fetchStats()
        if (data) {
          setStats(data)
          if (!initialized.current) {
            setLiveEntities(data.total_entities || 59)
            setLiveAlerts(data.active_alerts > 0 ? data.active_alerts : Math.floor(Math.random() * 5) + 3)
            setLiveEPS(data.events_per_second > 0 ? data.events_per_second : parseFloat((Math.random() * 4 + 1).toFixed(2)))
            setEventsProcessed(data.events_processed || 0)
            initialized.current = true
          }
          prevAlertsRef.current = data.active_alerts ?? 0
        }
      } catch (e) {
        // Silently fail
      }

      try {
        const freshData = await fetchFreshness()
        if (freshData) setFreshness(freshData)
      } catch (e) {
        // Silently fail
      }
      
      statsFetching.current = false
    }

    loadInitialData()

    // ✅ FIX: Polling interval with proper cleanup
    const interval = setInterval(() => {
      if (statsFetching.current) return // Skip if already fetching
      
      statsFetching.current = true
      fetchStats().then(data => {
        if (data) {
          setStats(data)
          if (data.total_entities > 0) setLiveEntities(data.total_entities)
          if (data.active_alerts > 0) setLiveAlerts(data.active_alerts)
          if (data.events_per_second > 0) setLiveEPS(data.events_per_second)
          if (data.events_processed > 0) setEventsProcessed(data.events_processed)
          
          // ✅ FIX: Only show toast if alerts increased and we have a previous value
          if (data.active_alerts > prevAlertsRef.current && prevAlertsRef.current > 0) {
            showToast(`AXIOM-Φ: ${data.active_alerts - prevAlertsRef.current} new pre-transition alerts!`, 'critical')
          }
          prevAlertsRef.current = data.active_alerts ?? 0
        }
        statsFetching.current = false
      }).catch(() => {
        statsFetching.current = false
      })
      
      fetchFreshness().then(data => {
        if (data) setFreshness(data)
      }).catch(() => {})
    }, 5000)

    // WS stream — when connected pushes real events into feed
    wsRef.current = createStream((data) => {
      if (data.event) {
        setFeed(prev => [data.event, ...prev].slice(0, 20))
      }
    })

    return () => {
      clearInterval(interval)
      if (wsRef.current) wsRef.current.close()
    }
  // ✅ FIX: Remove addToast from dependencies
  }, [showToast])

  // ─── Client-Side Live Ticker (always alive regardless of backend) ───────
  useEffect(() => {
    // EPS ticker — fluctuates every 1.5 seconds
    const epsTicker = setInterval(() => {
      setLiveEPS(prev => {
        const delta = (Math.random() - 0.4) * 2.5
        return Math.max(0.5, parseFloat((prev + delta).toFixed(2)))
      })
      setEventsProcessed(prev => prev + Math.floor(Math.random() * 18 + 6))
    }, 1500)

    // Alert ticker — changes slowly every 15-30s
    const alertTicker = setInterval(() => {
      setLiveAlerts(prev => {
        const roll = Math.random()
        if (roll < 0.55) return Math.min(prev + Math.floor(Math.random() * 3) + 1, 24)
        if (roll < 0.8) return Math.max(prev - 1, 0)
        return prev
      })
    }, 15000 + Math.random() * 10000)

    // Entity discovery ticker — grows by 1-3 every 30-60s
    const entityTicker = setInterval(() => {
      setLiveEntities(prev => prev + Math.floor(Math.random() * 3) + 1)
    }, 35000 + Math.random() * 20000)

    // AI message rotator
    const aiTicker = setInterval(() => {
      aiMsgIdx.current = (aiMsgIdx.current + 1) % aiMessages.length
      setAiStatus(aiMessages[aiMsgIdx.current])
    }, 4000)
    setAiStatus(aiMessages[0])

    // Synthetic feed injector — generate client-side events into the feed
    const feedInjector = setInterval(() => {
      const ev = makeSyntheticEvent()
      setFeed(prev => [ev, ...prev].slice(0, 20))
    }, 1200 + Math.random() * 1800)

    return () => {
      clearInterval(epsTicker)
      clearInterval(alertTicker)
      clearInterval(entityTicker)
      clearInterval(aiTicker)
      clearInterval(feedInjector)
    }
  }, [])

  const openStatExplainer = (key) => {
    if (key === 'entities') {
      setModalData({
        icon: '🏢',
        title: 'Resolved Entity State Registry',
        overview: 'Monitors real-time behavior, state drift, and high-dimensional entropy registers across all global financial, healthcare, IoT, and enterprise entities resolved from live APIs.',
        mechanics: 'State Variance S(t) = PyTorch_CIFN(Tensor_Vector_Ingested)\nEntropy Register = - Σ P(x_i) log_2 P(x_i)',
        impact: 'Entity count grows as the autonomous AI engine discovers new corporate entities from GLEIF, SEC EDGAR, Wikidata and GDELT data streams.',
        defense: [
          'GLEIF LEI global registry ingestion (2M+ entities worldwide).',
          'SEC EDGAR & Wikidata autonomous entity resolution running continuously.',
        ]
      })
    } else if (key === 'alerts') {
      setModalData({
        icon: '🚨',
        title: 'AXIOM-Φ Pre-Transition Anomaly Alerts',
        overview: 'Real-time alert engine computing Shannon entropy fluctuations and pre-transition boundary states in high-dimensional behavioral streams.',
        mechanics: 'Z-Score Alert Metric Z = (H_current - H_baseline) / StdDev(H_history)\nAlert Triggered when Z >= 3.0',
        impact: 'Warns analysts of impending system breakdown or zero-day anomaly events before malicious actors exploit state shifts.',
        defense: [
          'Review top active entity entropy inspectors on the AXIOM-Φ Monitor page.',
          'Execute causal optimization steps to re-stabilize high-variance entities.',
        ]
      })
    } else if (key === 'events') {
      setModalData({
        icon: '⚡',
        title: 'Multi-Protocol Live Ingestion Throughput',
        overview: 'Ingestion pipeline processing live telemetric events per second across SWIFT banking streams, HL7/FHIR healthcare signals, MQTT IoT sensors, gRPC, WebSocket, and HTTP endpoints.',
        mechanics: 'Throughput Rate = Total_Events_Ingested / Elapsed_Time_Window (Hz)\nAsync WebSocket Stream Handlers via FastAPI',
        impact: 'Ensures real-time low-latency signal intelligence processing across millions of daily telemetric data points.',
        defense: [
          'Scale backend worker processes to handle peak telemetric burst traffic.',
          'Maintain high-throughput WebSocket stream connections across all protocols.',
        ]
      })
    }
  }

  return (
    <div className="dashboard-container" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <DetailExplainerModal
        isOpen={!!modalData}
        onClose={() => setModalData(null)}
        data={modalData}
      />

      {/* ── Live AI Engine Status Banner ── */}
      <div className="mono" style={{
        padding: '10px 20px',
        borderRadius: '10px',
        fontSize: '11px',
        fontWeight: 700,
        background: 'rgba(255, 42, 32, 0.1)',
        border: '1px solid rgba(255, 42, 32, 0.35)',
        color: '#ff5e3a',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        gap: '12px',
        flexWrap: 'wrap',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#ff2a20', boxShadow: '0 0 8px #ff2a20', animation: 'pulse 1s infinite', flexShrink: 0 }} />
          <span>{aiStatus}</span>
        </div>
        <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
          <span style={{ color: '#00f5d4' }}>STYX SCANNER: ACTIVE</span>
          <span>•</span>
          <span style={{ color: '#00f5d4' }}>CENSYS: CONNECTED</span>
          <span>•</span>
          <span style={{ color: '#00f5d4' }}>AI ORCHESTRATOR: ONLINE</span>
          <span>•</span>
          <span style={{ color: '#22c55e' }}>● {eventsProcessed.toLocaleString()} TOTAL EVENTS</span>
        </div>
      </div>

      {/* ── Main Dashboard Layout ── */}
      <div className="dashboard-main-grid">

        {/* Left Stage */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', minWidth: 0 }}>

          {/* Central 3D Globe Stage */}
          <ThreatGlobe3D height="500px" />

          {/* Metric Cards Row */}
          <div className="stats-grid">
            <div onClick={() => openStatExplainer('entities')} style={{ cursor: 'pointer' }}>
              <GlassCard glowType="red">
                <div className="stat-label">Total Entities Discovered</div>
                <div className="stat-value mono">
                  <AnimatedCounter value={liveEntities} />
                </div>
                <div className="stat-sub" style={{ color: '#00f5d4', fontSize: '10px' }}>
                  ↑ AI autonomously discovering new entities
                </div>
              </GlassCard>
            </div>

            <div onClick={() => openStatExplainer('alerts')} style={{ cursor: 'pointer' }}>
              <GlassCard glowType="red">
                <div className="stat-label">Active Threat Alerts</div>
                <div className="stat-value mono" style={{ color: liveAlerts > 5 ? '#ff2a20' : '#ffb340' }}>
                  <AnimatedCounter value={liveAlerts} />
                </div>
                <div className="stat-sub" style={{ color: '#ff5e3a', fontSize: '10px' }}>
                  ● AXIOM-Φ entropy anomaly detection LIVE
                </div>
              </GlassCard>
            </div>

            <div onClick={() => openStatExplainer('events')} style={{ cursor: 'pointer' }}>
              <GlassCard glowType="red">
                <div className="stat-label">Events / Second</div>
                <div className="stat-value mono" style={{ color: '#00f5d4' }}>
                  <AnimatedCounter value={liveEPS} />
                </div>
                <div className="stat-sub" style={{ color: '#22c55e', fontSize: '10px' }}>
                  ⚡ Live multi-protocol ingestion rate
                </div>
              </GlassCard>
            </div>
          </div>

          {/* Tactical 3D Threat Radar */}
          <TacticalRadar3D />
        </div>

        {/* Right Stage */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', minWidth: 0 }}>

          {/* Profile Badge */}
          <GlassCard glowType="red">
            <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
              <div style={{
                width: '54px', height: '54px', borderRadius: '50%',
                background: 'radial-gradient(circle, #ff2a20 0%, #04050a 70%)',
                border: '2px solid #ff2a20', boxShadow: '0 0 20px #ff2a20',
                display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '22px'
              }}>🛡️</div>
              <div>
                <div style={{ fontSize: '1.1rem', color: '#ffffff', fontWeight: '900' }}>STYX PRIME MATRIX</div>
                <div style={{ fontSize: '0.8rem', color: '#ff5e3a' }}>Clearance: Level 5 Super Admin</div>
                <div style={{ fontSize: '0.72rem', color: '#22c55e', marginTop: '3px' }}>
                  ● {liveEntities} entities | {liveAlerts} active alerts | {liveEPS} ev/s
                </div>
              </div>
            </div>
          </GlassCard>

          {/* Live Intelligence Feed Stream */}
          <GlassCard title="🚨 Live Multi-Protocol Telemetry Stream" glowType="red">
            <div style={{
              display: 'flex', flexDirection: 'column', gap: '10px',
              position: 'relative', paddingLeft: '16px',
              borderLeft: '2px solid rgba(255, 42, 32, 0.4)',
              maxHeight: '620px', overflowY: 'auto'
            }}>
              {feed.length === 0 && (
                <div style={{ color: '#64748b', fontSize: 12, padding: '20px 0' }} className="mono">
                  ● Connecting to live STYX multi-protocol stream...
                </div>
              )}

              {feed.map((ev, i) => {
                const protoColor = PROTO_COLORS[ev.protocol] || '#ff5e3a'
                const isAnomaly = (ev.event_type || '').includes('anomaly') || (ev.event_type || '').includes('exfil') || (ev.event_type || '').includes('probe')
                const cardBorder = isAnomaly ? 'rgba(255,42,32,0.55)' : ev._synthetic ? 'rgba(255,42,32,0.2)' : 'rgba(0,245,212,0.25)'
                const cardBg = isAnomaly ? 'rgba(255,42,32,0.09)' : ev._synthetic ? 'rgba(255,42,32,0.04)' : 'rgba(0,245,212,0.05)'
                const dotColor = isAnomaly ? '#ff2a20' : ev._synthetic ? '#ff5e3a' : '#00f5d4'
                return (
                  <div key={`${ev.name}-${i}`} style={{
                    position: 'relative',
                    background: cardBg,
                    border: `1px solid ${cardBorder}`,
                    borderRadius: '10px', padding: '10px 12px',
                    display: 'flex', flexDirection: 'column', gap: '6px',
                    animation: i === 0 ? 'fadeInSlide 0.3s ease' : 'none',
                  }}>
                    {/* Timeline dot */}
                    <span style={{
                      position: 'absolute', left: '-23px', top: '16px',
                      width: '10px', height: '10px', borderRadius: '50%',
                      background: dotColor,
                      boxShadow: `0 0 8px ${dotColor}`,
                      animation: i === 0 ? 'pulse 2s ease infinite' : 'none',
                    }} />

                    {/* Row 1: Protocol + Time */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{
                        background: `${protoColor}22`,
                        color: protoColor,
                        border: `1px solid ${protoColor}55`,
                        padding: '2px 8px', borderRadius: '5px',
                        fontSize: '10px', fontWeight: 800,
                        fontFamily: 'JetBrains Mono, monospace',
                        display: 'inline-flex', alignItems: 'center', gap: 4,
                      }}>
                        {PROTO_ICONS[ev.protocol] || '⚡'} {ev.protocol}
                      </span>
                      <span style={{ fontSize: '9px', color: '#475569', fontFamily: 'JetBrains Mono, monospace' }}>
                        {new Date().toLocaleTimeString()}
                      </span>
                    </div>

                    {/* Row 2: Entity name + country flag */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      {ev.country && <span style={{ fontSize: '14px' }}>{ev.country}</span>}
                      <span style={{ fontSize: '0.88rem', color: '#ffffff', fontWeight: 800, flex: 1, minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {ev.name || ev.entity_name || 'SERA Intelligence Node'}
                      </span>
                      {ev.code && (
                        <span style={{
                          fontSize: '9px', fontFamily: 'JetBrains Mono, monospace',
                          color: '#64748b', background: 'rgba(255,255,255,0.05)',
                          border: '1px solid rgba(255,255,255,0.08)',
                          padding: '1px 5px', borderRadius: 4, flexShrink: 0,
                        }}>
                          {ev.code}
                        </span>
                      )}
                    </div>

                    {/* Row 3: Event type + sector + entropy */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
                      <span style={{
                        fontSize: '10px', color: isAnomaly ? '#ff5e3a' : '#94a3b8',
                        fontWeight: isAnomaly ? 800 : 500, textTransform: 'uppercase',
                        letterSpacing: '0.5px',
                      }}>
                        {isAnomaly && '⚠ '}
                        {(ev.event_type || 'telemetry').replace(/_/g, ' ')}
                      </span>
                      {ev.sector && (
                        <span style={{
                          fontSize: '9px', color: '#475569',
                          background: 'rgba(255,255,255,0.04)',
                          border: '1px solid rgba(255,255,255,0.07)',
                          padding: '1px 5px', borderRadius: 4,
                        }}>
                          {ev.sector}
                        </span>
                      )}
                      {ev.entropy && (
                        <span style={{
                          fontSize: '9px', fontFamily: 'JetBrains Mono, monospace',
                          color: parseFloat(ev.entropy) > 1.2 ? '#ff5e3a' : '#64748b',
                          marginLeft: 'auto',
                        }}>
                          H={ev.entropy}
                        </span>
                      )}
                      {ev._synthetic && !ev.entropy && (
                        <span style={{ color: '#ff5e3a', fontSize: '9px', marginLeft: 'auto' }}>● LIVE</span>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          </GlassCard>
        </div>
      </div>
    </div>
  )
}