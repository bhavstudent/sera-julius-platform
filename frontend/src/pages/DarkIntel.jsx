import { useEffect, useState } from 'react'
import { fetchDarkIntel } from '../api/client'
import GlassCard from '../components/GlassCard'

export default function DarkIntel() {
  const [intelList, setIntelList] = useState([])
  const [scanning, setScanning] = useState(true)

  useEffect(() => {
    fetchDarkIntel().then(data => {
      if (Array.isArray(data)) {
        setIntelList(data)
      } else if (data && data.briefings) {
        setIntelList(data.briefings)
      }
    }).catch(() => {})

    const timer = setTimeout(() => {
      setScanning(false)
    }, 1200)
    return () => clearTimeout(timer)
  }, [])

  const defaultItems = [
    { id: 1, title: 'SWIFT Network Zero-Day Exploit Trading Thread', severity: 'CRITICAL', source: 'BreachForums', date: '2026-07-24' },
    { id: 2, title: 'Leaked Corporate Credentials — 14.2M Records', severity: 'HIGH', source: 'XSS.is', date: '2026-07-24' },
    { id: 3, title: 'NTP Amplification DDoS Botnet Rental Market', severity: 'HIGH', source: 'Exploit.in', date: '2026-07-23' },
  ]

  const itemsToRender = intelList.length > 0 ? intelList : defaultItems

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Classified Header */}
      <GlassCard glowType="red">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <h2 style={{ margin: 0, fontSize: '1.4rem', color: '#ffffff', fontWeight: '900', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span>🕵️</span> CLASSIFIED DARK INTEL & THREAT FEED
            </h2>
            <span style={{ fontSize: '0.83rem', color: '#94a3b8' }}>
              Real-time Dark Web Forum Monitoring, Leaked Credential Registries & Exploits
            </span>
          </div>

          <span className="mono" style={{
            background: 'rgba(255, 42, 32, 0.2)',
            color: '#ff2a20',
            border: '1px solid #ff2a20',
            padding: '6px 14px',
            borderRadius: '12px',
            fontSize: '11px',
            fontWeight: '900',
            letterSpacing: '1px'
          }}>
            CLEARANCE: LEVEL 5 SUPER_ADMIN APPROVED
          </span>
        </div>
      </GlassCard>

      {/* Biometric Laser Scanner Gate Animation */}
      {scanning ? (
        <GlassCard glowType="red">
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '280px',
            gap: '16px'
          }}>
            <div style={{
              width: '70px',
              height: '70px',
              borderRadius: '50%',
              border: '3px solid #ff2a20',
              boxShadow: '0 0 30px #ff2a20',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '32px',
              animation: 'pulse 1s infinite'
            }}>
              👁️
            </div>
            <div className="mono" style={{ color: '#ff2a20', fontWeight: '900', fontSize: '13px', letterSpacing: '1.5px' }}>
              VERIFYING BIOMETRIC CLEARANCE & DECRYPTING INTEL...
            </div>
          </div>
        </GlassCard>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
          {itemsToRender.map((item, idx) => (
            <GlassCard key={item.id || idx} glowType="red">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <span className="mono" style={{ fontSize: '10px', color: '#ff5e3a', fontWeight: 'bold' }}>{item.source || 'CLASSIFIED'}</span>
                <span style={{
                  background: item.severity === 'CRITICAL' ? 'rgba(255, 42, 32, 0.25)' : 'rgba(255, 179, 64, 0.25)',
                  color: item.severity === 'CRITICAL' ? '#ff2a20' : '#ffb340',
                  padding: '3px 8px',
                  borderRadius: '4px',
                  fontSize: '9.5px',
                  fontWeight: 'bold'
                }}>
                  {item.severity || 'HIGH'}
                </span>
              </div>

              <h4 style={{ margin: '0 0 10px 0', fontSize: '1rem', color: '#ffffff', fontWeight: '800' }}>
                {item.title || item.headline || 'Classified Intelligence Payload'}
              </h4>

              <div style={{ fontSize: '0.8rem', color: '#94a3b8', display: 'flex', justifyContent: 'space-between' }}>
                <span>Timestamp: {item.date || 'Today'}</span>
                <span style={{ color: '#ff2a20', fontWeight: 'bold' }}>DECRYPTED</span>
              </div>
            </GlassCard>
          ))}
        </div>
      )}
    </div>
  )
}

