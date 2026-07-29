export default function GlassCard({ 
  children, 
  title, 
  glowType = '',
  className = '', 
  style = {},
  onClick
}) {
  const glowClass = glowType ? `glowing-${glowType}` : ''
  const cursorStyle = onClick ? { cursor: 'pointer' } : {}

  return (
    <div 
      className={`card glass-panel cyber-hud-card ${glowClass} ${className}`} 
      style={{ ...style, ...cursorStyle }}
      onClick={onClick}
    >
      <span className="hud-corner top-left" />
      <span className="hud-corner top-right" />
      <span className="hud-corner bottom-left" />
      <span className="hud-corner bottom-right" />
      <div className="cyber-scanline" />

      {title && (
        <div className="card-title">
          <span>{title}</span>
        </div>
      )}
      {children}
    </div>
  )
}
