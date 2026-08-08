import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { fetchZolaStatus } from '../api/client'

const links = [
  { path: '/dashboard', icon: '📊', label: 'Dashboard' },
  { path: '/omniscience', icon: '👁️', label: 'Omniscience Engine', badge: 'NEW' },
  { path: '/security', icon: '🛡️', label: 'Security Console', badge: 'STYX' },
  { path: '/zola', icon: '🔮', label: 'Causal Engine', badge: 'KRONOS' },
  { path: '/intel', icon: '🕵️', label: 'Dark Intel', badge: 'CLASSIFIED' },
  { path: '/entities', icon: '🏢', label: 'Entity Registry' },
  { path: '/synthesize', icon: '⚡', label: 'Signal Synthesis' },
  { path: '/graph', icon: '🕸️', label: 'Knowledge Graph' },
  { path: '/claims', icon: '⚖️', label: 'Claim Credibility' },
  { path: '/geo', icon: '🎯', label: 'Citation Tracking' },
  { path: '/axiom', icon: '∿', label: 'AXIOM-Φ Monitor' },
  { path: '/causal-graph', icon: '📐', label: 'Causal Geometry' },
  { path: '/healthcare', icon: '🏥', label: 'Healthcare CMS' },
  { path: '/executive', icon: '👔', label: 'Executive Intel' },
  { path: '/ai', icon: '💬', label: 'AI Command' },
]

export default function Sidebar({ collapsed, setCollapsed }) {
  const location = useLocation()
  const navigate = useNavigate()
  const [hoveredItem, setHoveredItem] = useState(null)
  const [zolaStatus, setZolaStatus] = useState(null)
  // On mobile (<768px) sidebar slides fully off-screen; this tracks overlay visibility
  const [mobileOpen, setMobileOpen] = useState(false)
  const isMobile = typeof window !== 'undefined' && window.innerWidth < 768

  useEffect(() => {
    fetchZolaStatus().then(setZolaStatus).catch(() => {})
  }, [])

  // Close mobile drawer when route changes
  useEffect(() => {
    setMobileOpen(false)
  }, [location.pathname])

  const handleNavClick = (path) => {
    navigate(path)
    if (window.innerWidth < 768) setMobileOpen(false)
  }

  const toggleCollapse = () => {
    if (window.innerWidth < 768) {
      setMobileOpen(prev => !prev)
    } else {
      setCollapsed && setCollapsed(prev => !prev)
    }
  }

  // On mobile, sidebar is always "hidden" unless mobileOpen
  const sidebarClass = [
    'sidebar',
    collapsed && window.innerWidth >= 768 ? 'collapsed' : '',
    window.innerWidth < 768 && !mobileOpen ? 'mobile-hidden' : '',
    window.innerWidth < 768 && mobileOpen ? 'mobile-open' : '',
  ].filter(Boolean).join(' ')

  return (
    <>
      {/* ── Hamburger Toggle Button (always visible) ── */}
      <button
        className="sidebar-toggle-btn"
        onClick={toggleCollapse}
        aria-label="Toggle sidebar"
      >
        <span className="hamburger-line" />
        <span className="hamburger-line" />
        <span className="hamburger-line" />
      </button>

      {/* ── Mobile Backdrop Overlay ── */}
      {mobileOpen && (
        <div
          className="sidebar-overlay"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* ── Sidebar Panel ── */}
      <aside className={sidebarClass}>
        {/* Brand Header */}
        <div className="sidebar-brand" onClick={() => handleNavClick('/dashboard')}>
          <div className="brand-logo-glow">🛡️</div>
          {(!collapsed || window.innerWidth < 768) && (
            <div className="brand-text">
              <div className="brand-name">CYBERSPACE</div>
              <div className="brand-sub">INTELLIGENCE PLATFORM</div>
            </div>
          )}
          {/* Collapse toggle arrow (desktop only) */}
          {window.innerWidth >= 768 && (
            <button
              className="collapse-arrow-btn"
              onClick={(e) => { e.stopPropagation(); setCollapsed && setCollapsed(p => !p) }}
              title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            >
              {collapsed ? '›' : '‹'}
            </button>
          )}
        </div>

        {/* Navigation Links */}
        <div className="sidebar-menu">
          {links.map(link => {
            const isActive = location.pathname === link.path
            return (
              <div
                key={link.path}
                className={`menu-item ${isActive ? 'active' : ''}`}
                title={collapsed && window.innerWidth >= 768 ? `${link.icon} ${link.label}` : ''}
                onClick={() => handleNavClick(link.path)}
                onMouseEnter={() => setHoveredItem(link.path)}
                onMouseLeave={() => setHoveredItem(null)}
              >
                <span className="menu-icon">{link.icon}</span>
                {(!collapsed || window.innerWidth < 768) && (
                  <span className="menu-label">{link.label}</span>
                )}
                {(!collapsed || window.innerWidth < 768) && link.badge && (
                  <span className={`menu-badge ${link.badge === 'STYX' ? 'crimson' : ''}`}>
                    {link.badge}
                  </span>
                )}

                {/* Tooltip on collapsed desktop */}
                {collapsed && window.innerWidth >= 768 && hoveredItem === link.path && (
                  <div className="hover-tooltip">
                    <span style={{ fontSize: '14px' }}>{link.icon}</span>
                    <span style={{ fontWeight: '800', letterSpacing: '0.5px' }}>{link.label}</span>
                    {link.badge && (
                      <span style={{
                        fontSize: '9px',
                        background: 'rgba(255, 42, 32, 0.3)',
                        color: '#ff2a20',
                        padding: '2px 6px',
                        borderRadius: '4px',
                        border: '1px solid rgba(255, 42, 32, 0.5)',
                        marginLeft: '4px'
                      }}>
                        {link.badge}
                      </span>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {/* Bottom Operational Status */}
        <div style={{
          padding: (collapsed && window.innerWidth >= 768) ? '12px 0' : '14px 20px',
          borderTop: '1px solid rgba(255, 42, 32, 0.2)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: (collapsed && window.innerWidth >= 768) ? 'center' : 'space-between',
          marginTop: 'auto'
        }}>
          {(!collapsed || window.innerWidth < 768) && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span className="live-pulse-dot" />
              <span className="mono" style={{ fontSize: '10px', color: '#10b981', fontWeight: 'bold' }}>
                OPERATIONAL
              </span>
            </div>
          )}
          {(collapsed && window.innerWidth >= 768) && (
            <span className="live-pulse-dot" title="OPERATIONAL" />
          )}
        </div>
      </aside>
    </>
  )
}
