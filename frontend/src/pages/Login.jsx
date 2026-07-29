import React, { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

// ── Mini particle canvas ────────────────────────────────────────────────────
function LoginParticles() {
  const canvasRef = useRef(null)
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    let animId

    const resize = () => {
      canvas.width = canvas.offsetWidth * devicePixelRatio
      canvas.height = canvas.offsetHeight * devicePixelRatio
      ctx.scale(devicePixelRatio, devicePixelRatio)
    }
    resize()
    window.addEventListener('resize', resize)

    const particles = Array.from({ length: 80 }, () => ({
      x: Math.random() * canvas.offsetWidth,
      y: Math.random() * canvas.offsetHeight,
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
      r: Math.random() * 1.5 + 0.5,
      alpha: Math.random() * 0.5 + 0.1
    }))

    const draw = () => {
      const w = canvas.offsetWidth, h = canvas.offsetHeight
      ctx.clearRect(0, 0, w, h)
      particles.forEach(p => {
        p.x += p.vx; p.y += p.vy
        if (p.x < 0 || p.x > w) p.vx *= -1
        if (p.y < 0 || p.y > h) p.vy *= -1
        ctx.beginPath()
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(255,42,32,${p.alpha})`
        ctx.fill()
      })
      // connections
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x
          const dy = particles[i].y - particles[j].y
          const dist = Math.sqrt(dx * dx + dy * dy)
          if (dist < 100) {
            ctx.beginPath()
            ctx.moveTo(particles[i].x, particles[i].y)
            ctx.lineTo(particles[j].x, particles[j].y)
            ctx.strokeStyle = `rgba(255,42,32,${0.12 * (1 - dist / 100)})`
            ctx.lineWidth = 0.5
            ctx.stroke()
          }
        }
      }
      animId = requestAnimationFrame(draw)
    }
    draw()
    return () => { cancelAnimationFrame(animId); window.removeEventListener('resize', resize) }
  }, [])
  return <canvas ref={canvasRef} style={{ position: 'absolute', inset: 0, width: '100%', height: '100%' }} />
}

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPass, setShowPass] = useState(false)
  const [focused, setFocused] = useState(null)
  const [mounted, setMounted] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  useEffect(() => { setTimeout(() => setMounted(true), 100) }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(username, password)
      navigate('/dashboard')
    } catch (err) {
      setError(err.message || 'Authentication failed. Check credentials.')
    } finally {
      setLoading(false)
    }
  }

  const handleDemo = () => {
    setUsername('admin')
    setPassword('AdminPass2026!')
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      fontFamily: "'Inter', -apple-system, sans-serif",
      background: '#020204',
      overflow: 'hidden'
    }}>
      <style>{`
        @keyframes shimmer-line { 0% { transform: translateX(-100%); } 100% { transform: translateX(200%); } }
        @keyframes glow-border { 0%,100% { box-shadow: 0 0 20px rgba(255,42,32,0.3); } 50% { box-shadow: 0 0 40px rgba(255,42,32,0.6); } }
        @keyframes fade-in-up { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } }
        @keyframes spin-slow { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        .login-input {
          width: 100%;
          padding: 14px 16px;
          background: rgba(4,7,18,0.7);
          border: 1px solid rgba(255,42,32,0.2);
          border-radius: 10px;
          color: #fff;
          font-size: 0.95rem;
          outline: none;
          transition: all 0.25s ease;
          font-family: inherit;
          box-sizing: border-box;
        }
        .login-input:focus {
          border-color: rgba(255,42,32,0.7);
          background: rgba(4,7,18,0.9);
          box-shadow: 0 0 0 3px rgba(255,42,32,0.1);
        }
        .login-input::placeholder { color: #334155; }
        .login-btn {
          width: 100%;
          padding: 15px;
          background: linear-gradient(135deg, #ff2a20, #ff5e3a);
          color: #fff;
          border: none;
          border-radius: 10px;
          font-weight: 800;
          font-size: 1rem;
          cursor: pointer;
          letter-spacing: 0.5px;
          transition: all 0.3s ease;
          position: relative;
          overflow: hidden;
        }
        .login-btn:not(:disabled):hover {
          transform: translateY(-1px);
          box-shadow: 0 8px 25px rgba(255,42,32,0.5);
        }
        .login-btn:disabled { opacity: 0.7; cursor: not-allowed; }
        .login-btn::after {
          content: '';
          position: absolute;
          top: 0; left: -100%; width: 60%; height: 100%;
          background: linear-gradient(90deg, transparent, rgba(255,255,255,0.25), transparent);
          transform: skewX(-20deg);
          animation: shimmer-line 2.5s ease infinite;
        }
      `}</style>

      {/* ── Left Panel: Branding ── */}
      <div style={{
        flex: '1 1 50%',
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '60px',
        background: 'radial-gradient(ellipse at 40% 50%, rgba(255,42,32,0.12) 0%, rgba(2,2,4,0.98) 70%)',
        borderRight: '1px solid rgba(255,42,32,0.1)',
        overflow: 'hidden'
      }}>
        <LoginParticles />

        {/* Content over particles */}
        <div style={{
          position: 'relative', zIndex: 1, textAlign: 'center', maxWidth: 460,
          opacity: mounted ? 1 : 0,
          transition: 'opacity 0.8s ease'
        }}>
          {/* Logo */}
          <div style={{
            width: 80, height: 80, margin: '0 auto 28px',
            background: 'linear-gradient(135deg, rgba(255,42,32,0.3), rgba(255,94,58,0.15))',
            border: '1px solid rgba(255,42,32,0.5)',
            borderRadius: 20,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '2.2rem',
            boxShadow: '0 0 40px rgba(255,42,32,0.4)',
            animation: 'glow-border 3s ease-in-out infinite'
          }}>🛡️</div>

          <h1 style={{
            fontSize: '3.2rem', fontWeight: 900, letterSpacing: '-1px',
            marginBottom: 12, lineHeight: 1.1
          }}>
            <span style={{
              background: 'linear-gradient(135deg, #fff 30%, rgba(255,42,32,0.8))',
              WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text'
            }}>SERA</span>
          </h1>
          <p style={{ color: '#64748b', fontSize: '0.85rem', letterSpacing: '3px', textTransform: 'uppercase', marginBottom: 32, fontWeight: 600 }}>
            Intelligence Platform
          </p>

          <p style={{ color: '#475569', fontSize: '0.95rem', lineHeight: 1.7, marginBottom: 40 }}>
            Real-time global corporate intelligence, threat detection, and AI-powered security assessment across 190+ countries.
          </p>

          {/* Live status indicators */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10, alignItems: 'center' }}>
            {[
              { dot: '#22c55e', text: '14 Live API Feeds Active' },
              { dot: '#22c55e', text: 'STYX Network Monitor Online' },
              { dot: '#22c55e', text: 'Self-Healing Engine Running' },
            ].map(({ dot, text }) => (
              <div key={text} style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: '0.8rem', color: '#475569' }}>
                <div style={{ width: 7, height: 7, borderRadius: '50%', background: dot, boxShadow: `0 0 8px ${dot}`, flexShrink: 0 }} />
                <span>{text}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Rotating ring decoration */}
        <div style={{
          position: 'absolute', width: 500, height: 500,
          border: '1px solid rgba(255,42,32,0.06)',
          borderRadius: '50%',
          bottom: '-100px', left: '-100px',
          animation: 'spin-slow 30s linear infinite'
        }} />
        <div style={{
          position: 'absolute', width: 300, height: 300,
          border: '1px solid rgba(255,42,32,0.08)',
          borderRadius: '50%',
          top: '-80px', right: '-80px',
          animation: 'spin-slow 20s linear infinite reverse'
        }} />
      </div>

      {/* ── Right Panel: Login Form ── */}
      <div style={{
        flex: '1 1 50%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '60px 48px',
        background: 'rgba(4,7,18,0.98)'
      }}>
        <div style={{
          width: '100%', maxWidth: 420,
          opacity: mounted ? 1 : 0,
          transform: mounted ? 'translateY(0)' : 'translateY(30px)',
          transition: 'all 0.8s cubic-bezier(0.34,1.56,0.64,1) 0.2s'
        }}>
          {/* Back to landing */}
          <button
            onClick={() => navigate('/')}
            style={{
              background: 'none', border: 'none', color: '#475569',
              cursor: 'pointer', fontSize: '0.8rem', marginBottom: 32,
              padding: 0, display: 'flex', alignItems: 'center', gap: 6,
              transition: 'color 0.2s'
            }}
            onMouseEnter={e => e.currentTarget.style.color = '#ff5e3a'}
            onMouseLeave={e => e.currentTarget.style.color = '#475569'}
          >
            ← Back to Home
          </button>

          <div style={{ marginBottom: 36 }}>
            <h2 style={{ fontSize: '1.8rem', fontWeight: 800, marginBottom: 8, letterSpacing: '-0.5px' }}>
              Welcome back
            </h2>
            <p style={{ color: '#475569', fontSize: '0.9rem' }}>
              Sign in to your SERA Intelligence Console
            </p>
          </div>

          {/* Error Banner */}
          {error && (
            <div style={{
              background: 'rgba(239,68,68,0.1)',
              border: '1px solid rgba(239,68,68,0.4)',
              color: '#f87171',
              padding: '12px 16px',
              borderRadius: 10,
              fontSize: '0.85rem',
              marginBottom: 20,
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              animation: 'fade-in-up 0.3s ease'
            }}>
              <span>⚠️</span> {error}
            </div>
          )}

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
            {/* Username */}
            <div>
              <label style={{ display: 'block', fontSize: '0.78rem', color: '#64748b', marginBottom: 8, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '1px' }}>
                Operator ID / Username
              </label>
              <div style={{ position: 'relative' }}>
                <span style={{
                  position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)',
                  fontSize: '1rem', opacity: 0.5
                }}>👤</span>
                <input
                  type="text"
                  className="login-input"
                  style={{ paddingLeft: 40 }}
                  value={username}
                  onChange={e => setUsername(e.target.value)}
                  placeholder="e.g. admin"
                  required
                  autoFocus
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label style={{ display: 'block', fontSize: '0.78rem', color: '#64748b', marginBottom: 8, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '1px' }}>
                Secret Access Key
              </label>
              <div style={{ position: 'relative' }}>
                <span style={{
                  position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)',
                  fontSize: '1rem', opacity: 0.5
                }}>🔑</span>
                <input
                  type={showPass ? 'text' : 'password'}
                  className="login-input"
                  style={{ paddingLeft: 40, paddingRight: 48 }}
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPass(!showPass)}
                  style={{
                    position: 'absolute', right: 14, top: '50%', transform: 'translateY(-50%)',
                    background: 'none', border: 'none', cursor: 'pointer',
                    color: '#475569', fontSize: '1rem', padding: 0,
                    transition: 'color 0.2s'
                  }}
                >
                  {showPass ? '🙈' : '👁️'}
                </button>
              </div>
            </div>

            {/* Submit */}
            <button
              type="submit"
              className="login-btn"
              disabled={loading}
              style={{ marginTop: 6 }}
            >
              {loading ? (
                <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10 }}>
                  <span style={{
                    width: 16, height: 16, border: '2px solid rgba(255,255,255,0.3)',
                    borderTopColor: '#fff', borderRadius: '50%',
                    display: 'inline-block', animation: 'spin-slow 0.8s linear infinite'
                  }} />
                  Authenticating...
                </span>
              ) : '🔐 Access Intelligence Console'}
            </button>

            {/* Demo credentials helper */}
            <div style={{
              background: 'rgba(255,42,32,0.06)',
              border: '1px solid rgba(255,42,32,0.2)',
              borderRadius: 10,
              padding: '14px 16px',
            }}>
              <div style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '1px', marginBottom: 8 }}>
                🎯 Demo Credentials
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ fontSize: '0.82rem', color: '#475569' }}>
                  <span style={{ color: '#ff5e3a', fontFamily: 'JetBrains Mono, monospace' }}>admin</span>
                  {' / '}
                  <span style={{ color: '#ff5e3a', fontFamily: 'JetBrains Mono, monospace' }}>AdminPass2026!</span>
                </div>
                <button
                  type="button"
                  onClick={handleDemo}
                  style={{
                    background: 'rgba(255,42,32,0.15)',
                    border: '1px solid rgba(255,42,32,0.3)',
                    color: '#ff5e3a',
                    padding: '5px 12px',
                    borderRadius: 6,
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,42,32,0.25)'}
                  onMouseLeave={e => e.currentTarget.style.background = 'rgba(255,42,32,0.15)'}
                >
                  Auto-fill
                </button>
              </div>
            </div>
          </form>

          {/* Footer */}
          <div style={{ marginTop: 32, textAlign: 'center', fontSize: '0.75rem', color: '#1e293b' }}>
            <span>SERA Intelligence Platform v4.2 • Authorized Personnel Only</span>
          </div>
        </div>
      </div>
    </div>
  )
}
