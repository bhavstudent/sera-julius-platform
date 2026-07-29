import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'

// ── 3D Particle Globe ────────────────────────────────────────────────────────
function ParticleGlobe() {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    let animId
    let t = 0

    const resize = () => {
      canvas.width = canvas.offsetWidth * window.devicePixelRatio
      canvas.height = canvas.offsetHeight * window.devicePixelRatio
      ctx.scale(window.devicePixelRatio, window.devicePixelRatio)
    }
    resize()
    window.addEventListener('resize', resize)

    const W = () => canvas.offsetWidth
    const H = () => canvas.offsetHeight
    const N_PARTICLES = 180
    const RADIUS = Math.min(W(), H()) * 0.38

    // Precompute spherical positions
    const particles = Array.from({ length: N_PARTICLES }, (_, i) => {
      const phi = Math.acos(1 - (2 * (i + 0.5)) / N_PARTICLES)
      const theta = Math.PI * (1 + Math.sqrt(5)) * i
      return { phi, theta, size: Math.random() * 1.5 + 0.5 }
    })

    // Connection pairs (close particles)
    const connections = []
    for (let i = 0; i < N_PARTICLES; i++) {
      for (let j = i + 1; j < N_PARTICLES; j++) {
        const a = particles[i], b = particles[j]
        const dx = Math.sin(a.phi)*Math.cos(a.theta) - Math.sin(b.phi)*Math.cos(b.theta)
        const dy = Math.sin(a.phi)*Math.sin(a.theta) - Math.sin(b.phi)*Math.sin(b.theta)
        const dz = Math.cos(a.phi) - Math.cos(b.phi)
        if (Math.sqrt(dx*dx + dy*dy + dz*dz) < 0.45) connections.push([i, j])
      }
    }

    const draw = () => {
      const w = W(), h = H()
      ctx.clearRect(0, 0, w, h)
      t += 0.004
      const cx = w / 2, cy = h / 2
      const r = Math.min(w, h) * 0.38

      // Compute 2D projected positions
      const pts = particles.map(p => {
        const x3 = Math.sin(p.phi) * Math.cos(p.theta + t)
        const y3 = Math.cos(p.phi)
        const z3 = Math.sin(p.phi) * Math.sin(p.theta + t)
        const persp = 1.6 / (1.6 - z3 * 0.5)
        return {
          x: cx + x3 * r * persp,
          y: cy + y3 * r * persp,
          z: z3,
          persp
        }
      })

      // Draw connections
      connections.forEach(([i, j]) => {
        const a = pts[i], b = pts[j]
        const avgZ = (a.z + b.z) / 2
        const alpha = Math.max(0, (avgZ + 1) / 2) * 0.35
        ctx.beginPath()
        ctx.moveTo(a.x, a.y)
        ctx.lineTo(b.x, b.y)
        ctx.strokeStyle = `rgba(255, 42, 32, ${alpha})`
        ctx.lineWidth = 0.5
        ctx.stroke()
      })

      // Draw nodes
      pts.forEach((p, i) => {
        const alpha = Math.max(0.1, (p.z + 1) / 2)
        const size = particles[i].size * p.persp
        const grad = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, size * 3)
        grad.addColorStop(0, `rgba(255, 42, 32, ${alpha})`)
        grad.addColorStop(0.5, `rgba(255, 94, 58, ${alpha * 0.5})`)
        grad.addColorStop(1, `rgba(255, 42, 32, 0)`)
        ctx.beginPath()
        ctx.arc(p.x, p.y, size * 3, 0, Math.PI * 2)
        ctx.fillStyle = grad
        ctx.fill()
        ctx.beginPath()
        ctx.arc(p.x, p.y, size * 0.8, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(255, 255, 255, ${alpha * 0.9})`
        ctx.fill()
      })

      // Ambient glow rings
      for (let ring = 0; ring < 3; ring++) {
        const ringR = r * (0.5 + ring * 0.22)
        const rStart = Math.max(0.1, ringR - 3)
        const rEnd = Math.max(0.2, ringR + 3)
        const grad2 = ctx.createRadialGradient(cx, cy, rStart, cx, cy, rEnd)
        grad2.addColorStop(0, `rgba(255, 42, 32, 0)`)
        grad2.addColorStop(0.5, `rgba(255, 42, 32, ${0.06 - ring * 0.015})`)
        grad2.addColorStop(1, `rgba(255, 42, 32, 0)`)
        ctx.beginPath()
        ctx.arc(cx, cy, ringR, 0, Math.PI * 2)
        ctx.strokeStyle = grad2
        ctx.lineWidth = 6
        ctx.stroke()
      }

      animId = requestAnimationFrame(draw)
    }
    draw()

    return () => {
      cancelAnimationFrame(animId)
      window.removeEventListener('resize', resize)
    }
  }, [])

  return <canvas ref={canvasRef} style={{ width: '100%', height: '100%', display: 'block' }} />
}

// ── Floating metric card ─────────────────────────────────────────────────────
function FloatingMetric({ icon, value, label, delay = 0, color = '#ff2a20' }) {
  const [visible, setVisible] = useState(false)
  useEffect(() => {
    const t = setTimeout(() => setVisible(true), delay)
    return () => clearTimeout(t)
  }, [delay])

  return (
    <div style={{
      background: 'rgba(8,8,13,0.85)',
      border: `1px solid ${color}40`,
      borderRadius: '12px',
      padding: '14px 18px',
      backdropFilter: 'blur(20px)',
      boxShadow: `0 0 20px ${color}20, inset 0 1px 0 rgba(255,255,255,0.05)`,
      transition: 'all 0.6s cubic-bezier(0.34,1.56,0.64,1)',
      opacity: visible ? 1 : 0,
      transform: visible ? 'translateY(0) scale(1)' : 'translateY(20px) scale(0.9)',
      minWidth: 130
    }}>
      <div style={{ fontSize: '1.4rem', marginBottom: 4 }}>{icon}</div>
      <div style={{ fontSize: '1.4rem', fontWeight: 900, color, letterSpacing: '-0.5px', fontFamily: 'JetBrains Mono, monospace' }}>{value}</div>
      <div style={{ fontSize: '0.7rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '1px', marginTop: 2 }}>{label}</div>
    </div>
  )
}

// ── Feature chip ─────────────────────────────────────────────────────────────
function FeatureChip({ icon, label }) {
  const [hovered, setHovered] = useState(false)
  return (
    <div
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        display: 'flex', alignItems: 'center', gap: 8,
        padding: '8px 14px',
        borderRadius: 8,
        border: `1px solid ${hovered ? 'rgba(255,42,32,0.6)' : 'rgba(255,42,32,0.2)'}`,
        background: hovered ? 'rgba(255,42,32,0.1)' : 'rgba(255,255,255,0.03)',
        cursor: 'default',
        transition: 'all 0.2s ease',
        fontSize: '0.8rem',
        color: hovered ? '#fff' : '#94a3b8',
        whiteSpace: 'nowrap'
      }}
    >
      <span style={{ fontSize: '1rem' }}>{icon}</span>
      <span style={{ fontWeight: 600 }}>{label}</span>
    </div>
  )
}

// ── Scan line animation ───────────────────────────────────────────────────────
function ScanLine() {
  return (
    <div style={{
      position: 'absolute', inset: 0, overflow: 'hidden', pointerEvents: 'none', zIndex: 0,
      borderRadius: 'inherit'
    }}>
      <style>{`
        @keyframes scan {
          0% { transform: translateY(-100%); opacity: 0; }
          10% { opacity: 1; }
          90% { opacity: 0.3; }
          100% { transform: translateY(800px); opacity: 0; }
        }
        @keyframes pulse-ring {
          0% { transform: scale(0.95); opacity: 0.8; }
          50% { transform: scale(1.05); opacity: 0.4; }
          100% { transform: scale(0.95); opacity: 0.8; }
        }
        @keyframes float-up {
          0%,100% { transform: translateY(0px); }
          50% { transform: translateY(-12px); }
        }
        @keyframes glow-pulse {
          0%,100% { box-shadow: 0 0 30px rgba(255,42,32,0.4), 0 0 60px rgba(255,42,32,0.2); }
          50% { box-shadow: 0 0 50px rgba(255,42,32,0.7), 0 0 100px rgba(255,42,32,0.3); }
        }
        @keyframes text-shimmer {
          0% { background-position: -200% center; }
          100% { background-position: 200% center; }
        }
        @keyframes counter-up {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .landing-btn-primary {
          background: linear-gradient(135deg, #ff2a20, #ff5e3a);
          color: #fff;
          border: none;
          padding: 16px 36px;
          border-radius: 10px;
          font-weight: 800;
          font-size: 1rem;
          cursor: pointer;
          letter-spacing: 0.5px;
          transition: all 0.3s ease;
          box-shadow: 0 8px 30px rgba(255,42,32,0.5);
          position: relative;
          overflow: hidden;
        }
        .landing-btn-primary:hover {
          transform: translateY(-2px);
          box-shadow: 0 12px 40px rgba(255,42,32,0.7);
        }
        .landing-btn-primary::before {
          content: '';
          position: absolute;
          inset: 0;
          background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
          transform: translateX(-100%);
          transition: transform 0.5s ease;
        }
        .landing-btn-primary:hover::before { transform: translateX(100%); }

        .landing-btn-secondary {
          background: rgba(255,255,255,0.05);
          color: #fff;
          border: 1px solid rgba(255,42,32,0.4);
          padding: 16px 36px;
          border-radius: 10px;
          font-weight: 700;
          font-size: 1rem;
          cursor: pointer;
          letter-spacing: 0.5px;
          transition: all 0.3s ease;
          backdrop-filter: blur(10px);
        }
        .landing-btn-secondary:hover {
          background: rgba(255,42,32,0.12);
          border-color: rgba(255,42,32,0.8);
          transform: translateY(-2px);
        }
      `}</style>
      <div style={{
        position: 'absolute', left: 0, right: 0, height: 2,
        background: 'linear-gradient(90deg, transparent, rgba(255,42,32,0.8), transparent)',
        animation: 'scan 4s ease-in-out infinite',
        animationDelay: '1s'
      }} />
    </div>
  )
}

// ── Main Landing Page ────────────────────────────────────────────────────────
export default function LandingPage() {
  const navigate = useNavigate()
  const [titleVisible, setTitleVisible] = useState(false)
  const [statsVisible, setStatsVisible] = useState(false)

  useEffect(() => {
    setTimeout(() => setTitleVisible(true), 200)
    setTimeout(() => setStatsVisible(true), 600)
  }, [])

  const features = [
    { icon: '🌍', label: '190+ Countries' },
    { icon: '⚡', label: 'Sub-2s Intelligence' },
    { icon: '🛡️', label: 'Threat Detection' },
    { icon: '🧠', label: 'AI-Powered Analysis' },
    { icon: '🔭', label: 'Dark Intel Briefings' },
    { icon: '📡', label: 'Live CVE Streams' },
    { icon: '🏢', label: '2M+ Legal Entities' },
    { icon: '🔐', label: 'Self-Healing Engine' },
  ]

  const stats = [
    { icon: '🛰️', value: '14', label: 'Live APIs', color: '#ff2a20', delay: 700 },
    { icon: '🌐', value: '2M+', label: 'Entities', color: '#ff5e3a', delay: 850 },
    { icon: '⚡', value: '<2s', label: 'Response', color: '#ffb340', delay: 1000 },
    { icon: '🛡️', value: '99%', label: 'Uptime', color: '#22c55e', delay: 1150 },
  ]

  return (
    <div style={{
      minHeight: '100vh',
      background: 'radial-gradient(ellipse at 20% 50%, rgba(255,42,32,0.07) 0%, transparent 50%), radial-gradient(ellipse at 80% 20%, rgba(131,56,236,0.06) 0%, transparent 50%), #020204',
      fontFamily: "'Inter', -apple-system, sans-serif",
      color: '#fff',
      overflow: 'hidden',
      position: 'relative'
    }}>
      <ScanLine />

      {/* Background grid */}
      <div style={{
        position: 'fixed', inset: 0, opacity: 0.03, zIndex: 0, pointerEvents: 'none',
        backgroundImage: 'linear-gradient(rgba(255,42,32,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(255,42,32,0.5) 1px, transparent 1px)',
        backgroundSize: '60px 60px'
      }} />

      {/* Nav Bar */}
      <nav style={{
        position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '18px 48px',
        background: 'rgba(2,2,4,0.85)',
        backdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(255,42,32,0.15)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{
            width: 36, height: 36, borderRadius: 8,
            background: 'linear-gradient(135deg, #ff2a20, #ff5e3a)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '1.1rem', boxShadow: '0 0 20px rgba(255,42,32,0.5)',
            animation: 'pulse-ring 3s ease-in-out infinite'
          }}>🛡️</div>
          <span style={{ fontWeight: 900, fontSize: '1.3rem', letterSpacing: '2px', color: '#fff' }}>
            SERA
            <span style={{ color: 'rgba(255,255,255,0.25)', fontWeight: 300, fontSize: '0.9rem', marginLeft: 6 }}>
              Intelligence Platform
            </span>
          </span>
        </div>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <span style={{ fontSize: '0.75rem', color: '#64748b', fontFamily: 'JetBrains Mono, monospace' }}>
            v4.2 PRODUCTION
          </span>
          <div style={{
            width: 8, height: 8, borderRadius: '50%',
            background: '#22c55e',
            boxShadow: '0 0 8px #22c55e',
            animation: 'pulse-ring 2s ease-in-out infinite'
          }} />
          <button
            onClick={() => navigate('/login')}
            className="landing-btn-primary"
            style={{ padding: '10px 24px', fontSize: '0.875rem' }}
          >
            Sign In →
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <div style={{
        display: 'flex', minHeight: '100vh',
        alignItems: 'center', justifyContent: 'center',
        padding: '100px 48px 60px',
        gap: 60, flexWrap: 'wrap'
      }}>
        {/* Left: Hero Copy */}
        <div style={{ flex: '1 1 480px', maxWidth: 620, zIndex: 1 }}>
          {/* Badge */}
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: 8,
            padding: '6px 14px',
            borderRadius: 100,
            border: '1px solid rgba(255,42,32,0.4)',
            background: 'rgba(255,42,32,0.08)',
            marginBottom: 28,
            fontSize: '0.75rem',
            color: '#ff5e3a',
            fontWeight: 700,
            letterSpacing: '1.5px',
            textTransform: 'uppercase',
            opacity: titleVisible ? 1 : 0,
            transition: 'all 0.6s ease',
            transform: titleVisible ? 'translateY(0)' : 'translateY(-10px)'
          }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#ff2a20', display: 'inline-block', boxShadow: '0 0 6px #ff2a20' }} />
            Live Intelligence Platform — 14 APIs Active
          </div>

          {/* Headline */}
          <h1 style={{
            fontSize: 'clamp(2.8rem, 5vw, 4.2rem)',
            fontWeight: 900,
            lineHeight: 1.08,
            marginBottom: 24,
            letterSpacing: '-1.5px',
            opacity: titleVisible ? 1 : 0,
            transition: 'all 0.8s ease 0.1s',
            transform: titleVisible ? 'translateY(0)' : 'translateY(20px)'
          }}>
            Real-Time<br />
            <span style={{
              background: 'linear-gradient(135deg, #ff2a20 0%, #ff5e3a 40%, #ffb340 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}>
              Global Intelligence
            </span>
            <br />
            at Your Fingertips
          </h1>

          {/* Sub-headline */}
          <p style={{
            fontSize: '1.05rem',
            color: '#94a3b8',
            lineHeight: 1.7,
            marginBottom: 36,
            maxWidth: 500,
            opacity: titleVisible ? 1 : 0,
            transition: 'all 0.8s ease 0.2s',
            transform: titleVisible ? 'translateY(0)' : 'translateY(20px)'
          }}>
            SERA aggregates <strong style={{ color: '#fff' }}>14 live APIs</strong> across 190+ countries — SEC filings, CVE threat streams, GLEIF entity data, GDELT geopolitical events — into a single real-time intelligence platform with AI-powered analysis and self-healing architecture.
          </p>

          {/* CTA Buttons */}
          <div style={{
            display: 'flex', gap: 14, flexWrap: 'wrap',
            opacity: titleVisible ? 1 : 0,
            transition: 'all 0.8s ease 0.3s',
            transform: titleVisible ? 'translateY(0)' : 'translateY(20px)'
          }}>
            <button className="landing-btn-primary" onClick={() => navigate('/login')}>
              🚀 Launch Platform
            </button>
            <button className="landing-btn-secondary" onClick={() => navigate('/login')}>
              View Live Demo
            </button>
          </div>

          {/* Feature chips */}
          <div style={{
            display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 32,
            opacity: titleVisible ? 1 : 0,
            transition: 'all 0.8s ease 0.4s',
          }}>
            {features.map(f => <FeatureChip key={f.label} {...f} />)}
          </div>
        </div>

        {/* Right: 3D Globe */}
        <div style={{
          flex: '1 1 400px', maxWidth: 560, height: 560,
          position: 'relative', zIndex: 1,
          animation: 'float-up 6s ease-in-out infinite',
          opacity: titleVisible ? 1 : 0,
          transition: 'opacity 1s ease 0.3s'
        }}>
          {/* Glow ring behind globe */}
          <div style={{
            position: 'absolute',
            inset: '15%',
            borderRadius: '50%',
            background: 'radial-gradient(ellipse, rgba(255,42,32,0.18) 0%, transparent 70%)',
            filter: 'blur(40px)',
            animation: 'glow-pulse 4s ease-in-out infinite'
          }} />
          <ParticleGlobe />

          {/* Floating stats cards */}
          <div style={{
            position: 'absolute', top: '8%', left: '-8%',
            display: 'flex', flexDirection: 'column', gap: 10
          }}>
            {stats.slice(0, 2).map(s => <FloatingMetric key={s.label} {...s} />)}
          </div>
          <div style={{
            position: 'absolute', bottom: '8%', right: '-8%',
            display: 'flex', flexDirection: 'column', gap: 10, alignItems: 'flex-end'
          }}>
            {stats.slice(2).map(s => <FloatingMetric key={s.label} {...s} />)}
          </div>
        </div>
      </div>

      {/* Bottom marquee */}
      <div style={{
        position: 'fixed', bottom: 0, left: 0, right: 0, zIndex: 50,
        background: 'rgba(2,2,4,0.95)',
        borderTop: '1px solid rgba(255,42,32,0.2)',
        padding: '10px 0',
        overflow: 'hidden'
      }}>
        <style>{`
          @keyframes marquee { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
        `}</style>
        <div style={{ display: 'flex', animation: 'marquee 30s linear infinite', width: 'max-content' }}>
          {[...Array(2)].map((_, ri) => (
            <span key={ri} style={{ display: 'flex', gap: 40, paddingRight: 40 }}>
              {['🔴 NVD NIST CVE Feed Active', '🌍 GLEIF 2M+ Entity Registry', '📡 GDELT Geopolitical Stream', '🏢 SEC EDGAR Filings Live', '⚡ IPinfo Geolocation Active', '🛡️ STYX Network Monitor Online', '🤖 AI Self-Healing Engine Active', '📊 14 APIs Connected'].map(item => (
                <span key={item} style={{ fontSize: '0.72rem', color: '#64748b', fontFamily: 'JetBrains Mono, monospace', whiteSpace: 'nowrap', letterSpacing: '0.5px' }}>
                  {item}
                </span>
              ))}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}
