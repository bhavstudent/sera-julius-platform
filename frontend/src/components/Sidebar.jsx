import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { fetchZolaStatus } from '../api/client'

// ── Navigation sections ───────────────────────────────────────────────────────
const sections = [
  {
    label: 'CORE INTELLIGENCE',
    links: [
      { path: '/dashboard',     icon: '📊', label: 'Dashboard' },
      { path: '/omniscience',   icon: '👁️', label: 'Omniscience Engine', badge: 'LIVE' },
      { path: '/zola',          icon: '🔮', label: 'Causal Engine',       badge: 'KRONOS' },
      { path: '/axiom',         icon: '∿',  label: 'AXIOM-Φ Monitor' },
      { path: '/entities',      icon: '🏢', label: 'Entity Registry' },
      { path: '/synthesize',    icon: '⚡', label: 'Signal Synthesis' },
      { path: '/graph',         icon: '🕸️', label: 'Knowledge Graph' },
      { path: '/claims',        icon: '⚖️', label: 'Claim Credibility' },
      { path: '/geo',           icon: '🎯', label: 'Citation Tracking' },
      { path: '/causal-graph',  icon: '📐', label: 'Causal Geometry' },
      { path: '/healthcare',    icon: '🏥', label: 'Healthcare CMS' },
      { path: '/executive',     icon: '👔', label: 'Executive Intel' },
    ],
  },
  {
    label: 'CYBER OPERATIONS',
    links: [
      { path: '/cyber-dashboard', icon: '🖥️', label: 'Cyber Dashboard',   badge: 'NEW' },
      { path: '/security',        icon: '🛡️', label: 'Security Console',   badge: 'STYX' },
      { path: '/scanner',         icon: '📡', label: 'Network Scanner',    badge: 'NEW' },
      { path: '/bgp-mitm',        icon: '🔀', label: 'BGP / MITM Ops',    badge: 'NEW' },
      { path: '/exploits',        icon: '💥', label: 'Exploit Framework',  badge: 'NEW' },
      { path: '/terminal',        icon: '⌨️', label: 'Remote Terminal',    badge: 'NEW' },
      { path: '/files',           icon: '📁', label: 'File Operations',    badge: 'NEW' },
      { path: '/tools',           icon: '🔧', label: 'Ops Toolkit',        badge: 'NEW' },
    ],
  },
  {
    label: 'INTELLIGENCE',
    links: [
      { path: '/intel',        icon: '🕵️', label: 'Dark Intel',          badge: 'CLASSIFIED' },
      { path: '/darkweb',      icon: '🌑', label: 'Dark Web OSINT',      badge: 'NEW' },
      { path: '/identity',     icon: '🪪', label: 'Identity Intel',      badge: 'NEW' },
      { path: '/signals',      icon: '📶', label: 'Signal Collection',   badge: 'NEW' },
      { path: '/threats',      icon: '⚠️', label: 'Threat Feeds',        badge: 'NEW' },
      { path: '/behavioral',   icon: '🧠', label: 'Behavioral Intel',    badge: 'NEW' },
      { path: '/insights-v2',  icon: '💡', label: 'Live Insights',       badge: 'NEW' },
      { path: '/events',       icon: '📋', label: 'Events Stream',       badge: 'NEW' },
      { path: '/monitor',      icon: '📺', label: 'Live Monitor',        badge: 'NEW' },
    ],
  },
  {
    label: 'AI & SYSTEMS',
    links: [
      { path: '/ai',          icon: '💬', label: 'AI Command' },
      { path: '/chat',        icon: '🤖', label: 'Julius Chat',          badge: 'NEW' },
      { path: '/guardian',    icon: '🦾', label: 'Guardian AI',          badge: 'NEW' },
      { path: '/ai-systems',  icon: '🔬', label: 'AI Systems',           badge: 'NEW' },
    ],
  },
  {
    label: 'INFRASTRUCTURE',
    links: [
      { path: '/veil',      icon: '🕶️', label: 'VEIL Anonymity',       badge: 'NEW' },
      { path: '/pantheon',  icon: '🏛️', label: 'Pantheon Engine',       badge: 'NEW' },
      { path: '/stratum',   icon: '🌐', label: 'Stratum OMNIS',         badge: 'NEW' },
      { path: '/settings',  icon: '⚙️', label: 'Settings',              badge: 'NEW' },
    ],
  },
]

export default function Sidebar({ collapsed, setCollapsed }) {
  const location = useLocation()
  const navigate = useNavigate()
  const [hoveredItem, setHoveredItem] = useState(null)
  const [zolaStatus, setZolaStatus] = useState(null)
  const [mobileOpen, setMobileOpen] = useState(false)
  const [expandedSections, setExpandedSections] = useState(() => {
    // All sections expanded by default
    return sections.reduce((acc, s) => ({ ...acc, [s.label]: true }), {})
  })

  useEffect(() => {
    fetchZolaStatus().then(setZolaStatus).catch(() => {})
  }, [])

  useEffect(() => { setMobileOpen(false) }, [location.pathname])

  const handleNavClick = (path) => {
    navigate(path)
    if (window.innerWidth < 768) setMobileOpen(false)
  }

  const toggleCollapse = () => {
    if (window.innerWidth < 768) setMobileOpen(prev => !prev)
    else setCollapsed && setCollapsed(prev => !prev)
  }

  const toggleSection = (label) => {
    setExpandedSections(prev => ({ ...prev, [label]: !prev[label] }))
  }

  const isCollapsed = collapsed && window.innerWidth >= 768

  const sidebarClass = [
    'sidebar',
    isCollapsed ? 'collapsed' : '',
    window.innerWidth < 768 && !mobileOpen ? 'mobile-hidden' : '',
    window.innerWidth < 768 && mobileOpen ? 'mobile-open' : '',
  ].filter(Boolean).join(' ')

  return (
    <>
      {/* Hamburger */}
      <button className="sidebar-toggle-btn" onClick={toggleCollapse} aria-label="Toggle sidebar">
        <span className="hamburger-line" />
        <span className="hamburger-line" />
        <span className="hamburger-line" />
      </button>

      {/* Mobile backdrop */}
      {mobileOpen && <div className="sidebar-overlay" onClick={() => setMobileOpen(false)} />}

      {/* Sidebar panel */}
      <aside className={sidebarClass}>
        {/* Brand */}
        <div className="sidebar-brand" onClick={() => handleNavClick('/dashboard')}>
          <div className="brand-logo-glow">🛡️</div>
          {!isCollapsed && (
            <div className="brand-text">
              <div className="brand-name">SERA</div>
              <div className="brand-sub">INTELLIGENCE PLATFORM</div>
            </div>
          )}
          {window.innerWidth >= 768 && (
            <button
              className="collapse-arrow-btn"
              onClick={e => { e.stopPropagation(); setCollapsed && setCollapsed(p => !p) }}
              title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            >
              {isCollapsed ? '›' : '‹'}
            </button>
          )}
        </div>

        {/* Navigation sections */}
        <div className="sidebar-menu" style={{ overflowY: 'auto', flex: 1 }}>
          {sections.map(section => (
            <div key={section.label}>
              {/* Section header */}
              {!isCollapsed && (
                <div
                  onClick={() => toggleSection(section.label)}
                  style={{
                    padding: '10px 16px 4px',
                    fontSize: '9px',
                    fontWeight: '800',
                    letterSpacing: '1.5px',
                    color: 'rgba(255,255,255,0.3)',
                    cursor: 'pointer',
                    userSelect: 'none',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  {section.label}
                  <span style={{ fontSize: '10px', color: 'rgba(255,255,255,0.2)' }}>
                    {expandedSections[section.label] ? '▾' : '▸'}
                  </span>
                </div>
              )}

              {/* Section links */}
              {(isCollapsed || expandedSections[section.label]) && section.links.map(link => {
                const isActive = location.pathname === link.path
                return (
                  <div
                    key={link.path}
                    className={`menu-item ${isActive ? 'active' : ''}`}
                    title={isCollapsed ? `${link.icon} ${link.label}` : ''}
                    onClick={() => handleNavClick(link.path)}
                    onMouseEnter={() => setHoveredItem(link.path)}
                    onMouseLeave={() => setHoveredItem(null)}
                  >
                    <span className="menu-icon">{link.icon}</span>
                    {!isCollapsed && <span className="menu-label">{link.label}</span>}
                    {!isCollapsed && link.badge && (
                      <span className={`menu-badge ${link.badge === 'STYX' || link.badge === 'CLASSIFIED' ? 'crimson' : link.badge === 'NEW' ? 'new-badge' : ''}`}>
                        {link.badge}
                      </span>
                    )}

                    {/* Collapsed tooltip */}
                    {isCollapsed && hoveredItem === link.path && (
                      <div className="hover-tooltip">
                        <span style={{ fontSize: '14px' }}>{link.icon}</span>
                        <span style={{ fontWeight: '800', letterSpacing: '0.5px' }}>{link.label}</span>
                        {link.badge && (
                          <span style={{
                            fontSize: '9px',
                            background: 'rgba(255,42,32,0.3)',
                            color: '#ff2a20',
                            padding: '2px 6px',
                            borderRadius: '4px',
                            border: '1px solid rgba(255,42,32,0.5)',
                            marginLeft: '4px'
                          }}>{link.badge}</span>
                        )}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          ))}
        </div>

        {/* Bottom status */}
        <div style={{
          padding: isCollapsed ? '12px 0' : '14px 20px',
          borderTop: '1px solid rgba(255,42,32,0.2)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: isCollapsed ? 'center' : 'space-between',
        }}>
          {!isCollapsed && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span className="live-pulse-dot" />
              <span className="mono" style={{ fontSize: '10px', color: '#10b981', fontWeight: 'bold' }}>
                OPERATIONAL
              </span>
            </div>
          )}
          {isCollapsed && <span className="live-pulse-dot" title="OPERATIONAL" />}
          {!isCollapsed && zolaStatus && (
            <span className="mono" style={{ fontSize: '9px', color: 'rgba(255,255,255,0.3)' }}>
              {zolaStatus.mode || 'ZOLA'}
            </span>
          )}
        </div>
      </aside>

      <style>{`
        .sidebar .menu-badge.new-badge {
          background: rgba(16, 185, 129, 0.15);
          color: #10b981;
          border: 1px solid rgba(16, 185, 129, 0.3);
        }
      `}</style>
    </>
  )
}
