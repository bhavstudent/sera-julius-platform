import { useState, useEffect } from 'react'
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

  useEffect(() => {
    const handleResize = () => {
      setCollapsed(window.innerWidth < 1200)
    }
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  return (
    <AuthProvider>
      <ToastProvider>
        <BrowserRouter>
          <ParticleBackground />
          <ThreatAlertBanner />
          <Routes>
            <Route path="/" element={<SmartRootRoute />} />
            <Route path="/landing" element={<LandingPage />} />
            <Route path="/login" element={<Login />} />
            <Route path="/dashboard" element={<ProtectedRoute><Layout path="/" collapsed={collapsed} setCollapsed={setCollapsed}><Dashboard /></Layout></ProtectedRoute>} />
            <Route path="/entities" element={<Layout path="/entities" collapsed={collapsed} setCollapsed={setCollapsed}><Entities /></Layout>} />
            <Route path="/entity/:ticker" element={<Layout path="/entity/:ticker" collapsed={collapsed} setCollapsed={setCollapsed}><EntityDetail /></Layout>} />
            <Route path="/synthesize" element={<Layout path="/synthesize" collapsed={collapsed} setCollapsed={setCollapsed}><SignalSynthesis /></Layout>} />
            <Route path="/graph" element={<Layout path="/graph" collapsed={collapsed} setCollapsed={setCollapsed}><EntityGraph /></Layout>} />
            <Route path="/claims" element={<Layout path="/claims" collapsed={collapsed} setCollapsed={setCollapsed}><ClaimCredibility /></Layout>} />
            <Route path="/geo" element={<Layout path="/geo" collapsed={collapsed} setCollapsed={setCollapsed}><CitationTracking /></Layout>} />
            <Route path="/axiom" element={<Layout path="/axiom" collapsed={collapsed} setCollapsed={setCollapsed}><AxiomMonitor /></Layout>} />
            <Route path="/zola" element={<Layout path="/zola" collapsed={collapsed} setCollapsed={setCollapsed}><ZolaPredictions /></Layout>} />
            <Route path="/ai" element={<Layout path="/ai" collapsed={collapsed} setCollapsed={setCollapsed}><AIAssistant /></Layout>} />
            <Route path="/intel" element={<ProtectedRoute><Layout path="/intel" collapsed={collapsed} setCollapsed={setCollapsed}><DarkIntel /></Layout></ProtectedRoute>} />
            <Route path="/causal-graph" element={<Layout path="/causal-graph" collapsed={collapsed} setCollapsed={setCollapsed}><CausalGraph /></Layout>} />
            <Route path="/healthcare" element={<Layout path="/healthcare" collapsed={collapsed} setCollapsed={setCollapsed}><Healthcare /></Layout>} />
            <Route path="/executive" element={<Layout path="/executive" collapsed={collapsed} setCollapsed={setCollapsed}><Executive /></Layout>} />
            <Route path="/security" element={<ProtectedRoute><Layout path="/security" collapsed={collapsed} setCollapsed={setCollapsed}><SecurityAssessment /></Layout></ProtectedRoute>} />
          </Routes>
        </BrowserRouter>
      </ToastProvider>
    </AuthProvider>
  )
}