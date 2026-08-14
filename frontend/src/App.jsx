import { useState, useEffect, useCallback, useMemo, lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import Dashboard from './pages/Dashboard'
import Entities from './pages/Entities'
import AxiomMonitor from './pages/AxiomMonitor'
import ZolaPredictions from './pages/ZolaPredictions'
import AIAssistant from './pages/AIAssistant'
import DarkIntel from './pages/DarkIntel'
import SignalSynthesis from './pages/SignalSynthesis'
import EntityGraph from './pages/EntityGraph'
import ClaimCredibility from './pages/ClaimCredibility'
import CitationTracking from './pages/CitationTracking'
import EntityDetail from './pages/EntityDetail'
import CausalGraph from './pages/CausalGraph'
import Healthcare from './pages/Healthcare'
import Executive from './pages/Executive'
import SecurityAssessment from './pages/SecurityAssessment'
import Omniscience from './pages/Omniscience'
import Login from './pages/Login'
import LandingPage from './pages/LandingPage'
import ParticleBackground from './components/ParticleBackground'
import ThreatAlertBanner from './components/ThreatAlertBanner'
import ProtectedRoute from './components/ProtectedRoute'
import { ToastProvider } from './components/ToastNotification'
import { AuthProvider, useAuth } from './context/AuthContext'

// ── Lazy-loaded new panel pages (code-split for performance) ──────────────────
const DashboardPanel    = lazy(() => import('./panels/DashboardPanel').then(m => ({ default: m.DashboardPanel })))
const BgpMitmPanel      = lazy(() => import('./panels/BgpMitmPanel').then(m => ({ default: m.BgpMitmPanel })))
const ScannerPanel      = lazy(() => import('./panels/ScannerPanel').then(m => ({ default: m.ScannerPanel })))
const ExploitsPanel     = lazy(() => import('./panels/ExploitsPanel').then(m => ({ default: m.ExploitsPanel })))
const DarkWebPanel      = lazy(() => import('./panels/DarkWebPanel').then(m => ({ default: m.DarkWebPanel })))
const TerminalPanel     = lazy(() => import('./panels/TerminalPanel').then(m => ({ default: m.TerminalPanel })))
const FilesPanel        = lazy(() => import('./panels/FilesPanel').then(m => ({ default: m.FilesPanel })))
const IdentityPanel     = lazy(() => import('./panels/IdentityPanel').then(m => ({ default: m.IdentityPanel })))
const VeilPanel         = lazy(() => import('./panels/VeilPanel').then(m => ({ default: m.VeilPanel })))
const PantheonPanel     = lazy(() => import('./panels/PantheonCommandCenterPanel').then(m => ({ default: m.PantheonCommandCenterPanel })))
const StratumOmnisPanel = lazy(() => import('./panels/StratumOmnisPanel').then(m => ({ default: m.StratumOmnisPanel })))
const MonitorPanel      = lazy(() => import('./panels/MonitorPanel').then(m => ({ default: m.MonitorPanel })))
const SignalCollection  = lazy(() => import('./panels/SignalCollectionPanel').then(m => ({ default: m.SignalCollectionPanel })))
const ThreatFeeds       = lazy(() => import('./panels/ThreatFeedsPanel').then(m => ({ default: m.ThreatFeedsPanel })))
const GuardianDash      = lazy(() => import('./panels/GuardianDashboard').then(m => ({ default: m.GuardianDashboard })))
const AISystems         = lazy(() => import('./panels/AISystems'))
const BehavioralPanel   = lazy(() => import('./panels/BehavioralPanel').then(m => ({ default: m.BehavioralPanel })))
const InsightsPanel     = lazy(() => import('./panels/InsightsPanel').then(m => ({ default: m.InsightsPanel })))
const EventsPanel       = lazy(() => import('./panels/EventsPanel').then(m => ({ default: m.EventsPanel })))
const ToolsPanel        = lazy(() => import('./panels/ToolsPanel').then(m => ({ default: m.ToolsPanel })))
const SettingsPanel     = lazy(() => import('./panels/SettingsPanel').then(m => ({ default: m.SettingsPanel })))
const ChatPanel         = lazy(() => import('./panels/ChatPanel').then(m => ({ default: m.ChatPanel })))

// ── Page metadata ─────────────────────────────────────────────────────────────
const pages = {
  '/':                   { title: 'SERA Platform', subtitle: 'Intelligence & Cyberops Command Center' },
  '/dashboard':          { title: 'SERA Dashboard', subtitle: 'Real-time multi-protocol intelligence overview' },
  '/cyber-dashboard':    { title: 'Cyber Dashboard', subtitle: 'Live cyberops situational awareness' },
  '/entities':           { title: 'Entity Registry', subtitle: 'Resolved profiles & state stability registers' },
  '/entity/:ticker':     { title: 'Corporate Intelligence Briefing', subtitle: 'Dynamic 360° entity profiling & predictive insights' },
  '/synthesize':         { title: 'Signal Synthesis Console', subtitle: 'Synthesized multi-source causal intelligence fusion' },
  '/graph':              { title: 'Entity Knowledge Graph', subtitle: 'Semantic relationship registry & 1-hop traversals' },
  '/claims':             { title: 'Claim Credibility (ALETHEIA)', subtitle: 'Stake-weighted adversarial truth verification' },
  '/geo':                { title: 'Citation Tracking (GEO)', subtitle: 'Generative Engine Optimization citation Share of Voice' },
  '/axiom':              { title: 'AXIOM-Φ Monitor', subtitle: 'Shannon entropy & pre-transition detection alerts' },
  '/zola':               { title: 'ZOLA Causal Engine', subtitle: 'Behavioral predictions & KRONOS self-evolution' },
  '/ai':                 { title: 'AI Command Console', subtitle: 'Natural language interface to platform subsystems' },
  '/intel':              { title: 'Dark Intel Briefings', subtitle: 'Classified behavioral intelligence briefings (Clearance Required)' },
  '/causal-graph':       { title: 'APEX Causal Geometry', subtitle: 'Interactive force-directed property graph visualizations' },
  '/healthcare':         { title: 'Healthcare CMS Dashboard', subtitle: 'Hospital admissions, Medicare spending, and pharmaceutical metrics' },
  '/executive':          { title: 'Executive Intelligence Briefing', subtitle: 'Public corporate leadership transitions and alignments' },
  '/security':           { title: 'Security Assessment Console', subtitle: 'Multi-agent authorized pentest pipeline' },
  '/omniscience':        { title: 'Omniscience Global Engine', subtitle: 'Unified Real-Time Perception • RAG Vector Memory • Guardian Remediation' },
  '/bgp-mitm':           { title: 'BGP/MITM Operations', subtitle: 'BGP hijacking detection, ARP/DNS spoofing, packet analysis' },
  '/scanner':            { title: 'Network Scanner', subtitle: 'Autonomous port & service discovery engine' },
  '/exploits':           { title: 'Exploit Framework', subtitle: 'Authorized exploit discovery and execution pipeline' },
  '/darkweb':            { title: 'Dark Web OSINT', subtitle: 'Tor-based intelligence collection & dark web monitoring' },
  '/terminal':           { title: 'Remote Terminal', subtitle: 'Secure remote shell execution console' },
  '/files':              { title: 'File Operations', subtitle: 'Remote file browser, transfer & management' },
  '/identity':           { title: 'Identity Intelligence', subtitle: 'Person entity extraction, verification & relationship graphs' },
  '/veil':               { title: 'VEIL Anonymity System', subtitle: 'Post-quantum KEM • Tor routing • Mixnet • Escrow operations' },
  '/pantheon':           { title: 'Pantheon Command Center', subtitle: 'Policy engine • Module health • Contract management • Audit log' },
  '/stratum':            { title: 'Stratum OMNIS Engine', subtitle: 'Categorical sheaf-theoretic intelligence (CSIE) • Entity resolution' },
  '/monitor':            { title: 'Live Monitor', subtitle: 'Global surveillance: map, TV feeds, news ticker, keyword tracking' },
  '/signals':            { title: 'Signal Collection', subtitle: 'Multi-source intelligence signal orchestration & enrichment' },
  '/threats':            { title: 'Threat Intelligence Feeds', subtitle: 'Real-time threat data aggregation from global sources' },
  '/guardian':           { title: 'Guardian AI Dashboard', subtitle: 'Autonomous threat detection & remediation agent status' },
  '/ai-systems':         { title: 'AI Systems Control', subtitle: 'All AI subsystem health, models, and orchestration status' },
  '/behavioral':         { title: 'Behavioral Intelligence', subtitle: 'Pattern recognition, anomaly detection & behavioral scoring' },
  '/insights-v2':        { title: 'Live Insights', subtitle: 'AI-generated real-time intelligence narrative engine' },
  '/events':             { title: 'Events Stream', subtitle: 'Live filtered event stream across all subsystems' },
  '/tools':              { title: 'Operations Toolkit', subtitle: 'Unified launcher for all offensive & defensive tools' },
  '/settings':           { title: 'Platform Settings', subtitle: 'System configuration, API keys, and operational parameters' },
  '/chat':               { title: 'Julius Chat', subtitle: 'Embedded Julius AI conversational intelligence interface' },
}

// Loading fallback for lazy panels
function PanelLoader() {
  return (
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      height: '60vh', flexDirection: 'column', gap: '16px'
    }}>
      <div style={{
        width: '40px', height: '40px', border: '3px solid rgba(255,42,32,0.3)',
        borderTop: '3px solid #ff2a20', borderRadius: '50%',
        animation: 'spin 0.8s linear infinite'
      }} />
      <span style={{ color: 'rgba(255,255,255,0.5)', fontSize: '13px', fontFamily: 'monospace' }}>
        LOADING MODULE...
      </span>
    </div>
  )
}

// Redirects authenticated users to /dashboard, else shows landing page
function SmartRootRoute() {
  const { isAuthenticated } = useAuth()
  return isAuthenticated ? <Navigate to="/dashboard" replace /> : <LandingPage />
}

// Memoized Layout component
function Layout({ path, collapsed, setCollapsed, children }) {
  const meta = pages[path] || pages['/']
  return (
    <div className={`app-layout ${collapsed ? 'sidebar-collapsed' : ''}`}>
      <Sidebar collapsed={collapsed} setCollapsed={setCollapsed} />
      <Header title={meta.title} subtitle={meta.subtitle} />
      <main className="main-content">{children}</main>
    </div>
  )
}

// Lazy panel wrapped in Suspense inside Layout
function LazyPage({ Component, path, collapsed, setCollapsed }) {
  return (
    <Layout path={path} collapsed={collapsed} setCollapsed={setCollapsed}>
      <Suspense fallback={<PanelLoader />}>
        <Component />
      </Suspense>
    </Layout>
  )
}

export default function App() {
  const [collapsed, setCollapsed] = useState(() => window.innerWidth < 1200)

  const handleResize = useCallback(() => {
    setCollapsed(window.innerWidth < 1200)
  }, [])

  useEffect(() => {
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [handleResize])

  const renderWithLayout = useCallback((Component, path) => (
    <Layout path={path} collapsed={collapsed} setCollapsed={setCollapsed}>
      <Component />
    </Layout>
  ), [collapsed])

  const renderLazy = useCallback((Component, path) => (
    <LazyPage Component={Component} path={path} collapsed={collapsed} setCollapsed={setCollapsed} />
  ), [collapsed])

  const routes = useMemo(() => (
    <Routes>
      {/* ── Public ── */}
      <Route path="/" element={<SmartRootRoute />} />
      <Route path="/landing" element={<LandingPage />} />
      <Route path="/login" element={<Login />} />

      {/* ── Core Intelligence ── */}
      <Route path="/dashboard" element={<ProtectedRoute>{renderWithLayout(Dashboard, '/dashboard')}</ProtectedRoute>} />
      <Route path="/entities" element={renderWithLayout(Entities, '/entities')} />
      <Route path="/entity/:ticker" element={renderWithLayout(EntityDetail, '/entity/:ticker')} />
      <Route path="/synthesize" element={renderWithLayout(SignalSynthesis, '/synthesize')} />
      <Route path="/graph" element={renderWithLayout(EntityGraph, '/graph')} />
      <Route path="/claims" element={renderWithLayout(ClaimCredibility, '/claims')} />
      <Route path="/geo" element={renderWithLayout(CitationTracking, '/geo')} />
      <Route path="/axiom" element={renderWithLayout(AxiomMonitor, '/axiom')} />
      <Route path="/zola" element={renderWithLayout(ZolaPredictions, '/zola')} />
      <Route path="/causal-graph" element={renderWithLayout(CausalGraph, '/causal-graph')} />
      <Route path="/healthcare" element={renderWithLayout(Healthcare, '/healthcare')} />
      <Route path="/executive" element={renderWithLayout(Executive, '/executive')} />
      <Route path="/omniscience" element={renderWithLayout(Omniscience, '/omniscience')} />

      {/* ── Protected Core ── */}
      <Route path="/ai" element={<ProtectedRoute>{renderWithLayout(AIAssistant, '/ai')}</ProtectedRoute>} />
      <Route path="/intel" element={<ProtectedRoute>{renderWithLayout(DarkIntel, '/intel')}</ProtectedRoute>} />
      <Route path="/security" element={<ProtectedRoute>{renderWithLayout(SecurityAssessment, '/security')}</ProtectedRoute>} />

      {/* ── NEW: Cyber Operations (all protected) ── */}
      <Route path="/cyber-dashboard" element={<ProtectedRoute>{renderLazy(DashboardPanel, '/cyber-dashboard')}</ProtectedRoute>} />
      <Route path="/bgp-mitm" element={<ProtectedRoute>{renderLazy(BgpMitmPanel, '/bgp-mitm')}</ProtectedRoute>} />
      <Route path="/scanner" element={<ProtectedRoute>{renderLazy(ScannerPanel, '/scanner')}</ProtectedRoute>} />
      <Route path="/exploits" element={<ProtectedRoute>{renderLazy(ExploitsPanel, '/exploits')}</ProtectedRoute>} />
      <Route path="/darkweb" element={<ProtectedRoute>{renderLazy(DarkWebPanel, '/darkweb')}</ProtectedRoute>} />
      <Route path="/terminal" element={<ProtectedRoute>{renderLazy(TerminalPanel, '/terminal')}</ProtectedRoute>} />
      <Route path="/files" element={<ProtectedRoute>{renderLazy(FilesPanel, '/files')}</ProtectedRoute>} />

      {/* ── NEW: Intelligence ── */}
      <Route path="/identity" element={<ProtectedRoute>{renderLazy(IdentityPanel, '/identity')}</ProtectedRoute>} />
      <Route path="/signals" element={<ProtectedRoute>{renderLazy(SignalCollection, '/signals')}</ProtectedRoute>} />
      <Route path="/threats" element={<ProtectedRoute>{renderLazy(ThreatFeeds, '/threats')}</ProtectedRoute>} />
      <Route path="/behavioral" element={renderLazy(BehavioralPanel, '/behavioral')} />
      <Route path="/insights-v2" element={renderLazy(InsightsPanel, '/insights-v2')} />
      <Route path="/events" element={renderLazy(EventsPanel, '/events')} />

      {/* ── NEW: AI & Systems ── */}
      <Route path="/guardian" element={<ProtectedRoute>{renderLazy(GuardianDash, '/guardian')}</ProtectedRoute>} />
      <Route path="/ai-systems" element={<ProtectedRoute>{renderLazy(AISystems, '/ai-systems')}</ProtectedRoute>} />
      <Route path="/chat" element={<ProtectedRoute>{renderLazy(ChatPanel, '/chat')}</ProtectedRoute>} />

      {/* ── NEW: Infrastructure ── */}
      <Route path="/veil" element={<ProtectedRoute>{renderLazy(VeilPanel, '/veil')}</ProtectedRoute>} />
      <Route path="/pantheon" element={<ProtectedRoute>{renderLazy(PantheonPanel, '/pantheon')}</ProtectedRoute>} />
      <Route path="/stratum" element={<ProtectedRoute>{renderLazy(StratumOmnisPanel, '/stratum')}</ProtectedRoute>} />
      <Route path="/monitor" element={<ProtectedRoute>{renderLazy(MonitorPanel, '/monitor')}</ProtectedRoute>} />
      <Route path="/tools" element={<ProtectedRoute>{renderLazy(ToolsPanel, '/tools')}</ProtectedRoute>} />
      <Route path="/settings" element={<ProtectedRoute>{renderLazy(SettingsPanel, '/settings')}</ProtectedRoute>} />
    </Routes>
  ), [renderWithLayout, renderLazy])

  return (
    <AuthProvider>
      <ToastProvider>
        <BrowserRouter>
          <style>{`
            @keyframes spin { to { transform: rotate(360deg); } }
          `}</style>
          <ParticleBackground />
          <ThreatAlertBanner />
          {routes}
        </BrowserRouter>
      </ToastProvider>
    </AuthProvider>
  )
}
