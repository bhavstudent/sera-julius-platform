import { useState, useEffect, useCallback, useMemo } from 'react'
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
import Login from './pages/Login'
import LandingPage from './pages/LandingPage'
import ParticleBackground from './components/ParticleBackground'
import ThreatAlertBanner from './components/ThreatAlertBanner'
import ProtectedRoute from './components/ProtectedRoute'
import { ToastProvider } from './components/ToastNotification'
import { AuthProvider, useAuth } from './context/AuthContext'

// Redirects authenticated users to /dashboard, else shows landing page
function SmartRootRoute() {
  const { isAuthenticated } = useAuth()
  return isAuthenticated ? <Navigate to="/dashboard" replace /> : <LandingPage />
}

// ✅ FIX: Memoized page metadata to prevent re-creation on each render
const pages = {
  '/': { title: 'SERA Dashboard', subtitle: 'Real-time multi-protocol intelligence overview' },
  '/entities': { title: 'Entity Registry', subtitle: 'Resolved profiles & state stability registers' },
  '/entity/:ticker': { title: 'Corporate Intelligence Briefing', subtitle: 'Dynamic 360° entity profiling & predictive insights' },
  '/synthesize': { title: 'Signal Synthesis Console', subtitle: 'Synthesized multi-source causal intelligence fusion' },
  '/graph': { title: 'Entity Knowledge Graph', subtitle: 'Semantic relationship registry & 1-hop traversals' },
  '/claims': { title: 'Claim Credibility (ALETHEIA)', subtitle: 'Stake-weighted adversarial truth verification' },
  '/geo': { title: 'Citation Tracking (GEO)', subtitle: 'Generative Engine Optimization citation Share of Voice' },
  '/axiom': { title: 'AXIOM-Φ Monitor', subtitle: 'Shannon entropy & pre-transition detection alerts' },
  '/zola': { title: 'ZOLA Causal Engine', subtitle: 'Behavioral predictions & KRONOS self-evolution' },
  '/ai': { title: 'AI Command Console', subtitle: 'Natural language interface to platform subsystems' },
  '/intel': { title: 'Dark Intel Briefings', subtitle: 'Classified behavioral intelligence briefings (Clearance Required)' },
  '/causal-graph': { title: 'APEX Causal Geometry', subtitle: 'Interactive force-directed property graph visualizations' },
  '/healthcare': { title: 'Healthcare CMS Dashboard', subtitle: 'Hospital admissions, Medicare spending, and pharmaceutical metrics by state' },
  '/executive': { title: 'Executive Intelligence Briefing', subtitle: 'Public corporate leadership transitions and alignments from LinkedIn' },
  '/security': { title: 'Security Assessment Console', subtitle: 'Multi-agent authorized pentest pipeline — Recon → Analysis → Validation → Human Approval → Report' }
}

// ✅ FIX: Memoized Layout component to prevent unnecessary re-renders
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

export default function App() {
  // Automatic screen responsiveness (collapses when screen width < 1200px)
  const [collapsed, setCollapsed] = useState(() => window.innerWidth < 1200)

  // ✅ FIX: Use useCallback for resize handler
  const handleResize = useCallback(() => {
    setCollapsed(window.innerWidth < 1200)
  }, [])

  useEffect(() => {
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [handleResize])

  // ✅ FIX: Memoize the Layout wrapper to prevent re-renders
  const renderWithLayout = useCallback((Component, path) => {
    return (
      <Layout path={path} collapsed={collapsed} setCollapsed={setCollapsed}>
        <Component />
      </Layout>
    )
  }, [collapsed])

  // ✅ FIX: Memoize routes to prevent unnecessary re-creation
  const routes = useMemo(() => (
    <Routes>
      <Route path="/" element={<SmartRootRoute />} />
      <Route path="/landing" element={<LandingPage />} />
      <Route path="/login" element={<Login />} />
      <Route path="/dashboard" element={
        <ProtectedRoute>
          {renderWithLayout(Dashboard, '/')}
        </ProtectedRoute>
      } />
      <Route path="/entities" element={renderWithLayout(Entities, '/entities')} />
      <Route path="/entity/:ticker" element={renderWithLayout(EntityDetail, '/entity/:ticker')} />
      <Route path="/synthesize" element={renderWithLayout(SignalSynthesis, '/synthesize')} />
      <Route path="/graph" element={renderWithLayout(EntityGraph, '/graph')} />
      <Route path="/claims" element={renderWithLayout(ClaimCredibility, '/claims')} />
      <Route path="/geo" element={renderWithLayout(CitationTracking, '/geo')} />
      <Route path="/axiom" element={renderWithLayout(AxiomMonitor, '/axiom')} />
      <Route path="/zola" element={renderWithLayout(ZolaPredictions, '/zola')} />
      <Route path="/ai" element={renderWithLayout(AIAssistant, '/ai')} />
      <Route path="/intel" element={
        <ProtectedRoute>
          {renderWithLayout(DarkIntel, '/intel')}
        </ProtectedRoute>
      } />
      <Route path="/causal-graph" element={renderWithLayout(CausalGraph, '/causal-graph')} />
      <Route path="/healthcare" element={renderWithLayout(Healthcare, '/healthcare')} />
      <Route path="/executive" element={renderWithLayout(Executive, '/executive')} />
      <Route path="/security" element={
        <ProtectedRoute>
          {renderWithLayout(SecurityAssessment, '/security')}
        </ProtectedRoute>
      } />
    </Routes>
  ), [renderWithLayout])

  return (
    <AuthProvider>
      <ToastProvider>
        <BrowserRouter>
          <ParticleBackground />
          <ThreatAlertBanner />
          {routes}
        </BrowserRouter>
      </ToastProvider>
    </AuthProvider>
  )
}