import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'

export default function Header({ title, subtitle }) {
  const [time, setTime] = useState('')
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    const updateTime = () => {
      const now = new Date()
      setTime(now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) + ' | ' + now.toLocaleDateString(undefined, { month: 'short', day: 'numeric' }))
    }
    updateTime()
    const interval = setInterval(updateTime, 1000)
    return () => clearInterval(interval)
  }, [])

  return (
    <header className="app-header">
      <div className="header-left">
        <h1 className="header-page-title">{title}</h1>
        {subtitle && <p className="header-page-sub">{subtitle}</p>}
      </div>

      <div className="header-right">
        <div className="header-time mono">
          {time}
        </div>

        <div className="header-pill telemetry-live">
          <span className="live-pulse-dot" />
          <span>CYBER TELEMETRY LIVE</span>
        </div>

        <div className="header-pill styx-active">
          <span>🛡️ STYX PRIME</span>
        </div>

        {user && (
          <div className="header-user-badge">
            <span className="user-role-chip">
              👤 {user.username} <b style={{ color: '#ff2a20' }}>({user.role})</b>
            </span>
            <button className="logout-btn" onClick={() => { logout(); navigate('/login') }}>
              Logout
            </button>
          </div>
        )}
      </div>
    </header>
  )
}
