import React from 'react'

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    console.error('[SERA ErrorBoundary] Caught exception:', error, errorInfo)
  }

  handleReload = () => {
    this.setState({ hasError: false, error: null })
    window.location.reload()
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          minHeight: '100vh',
          background: '#04050a',
          color: '#ffffff',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '24px',
          fontFamily: "'Inter', sans-serif"
        }}>
          <div style={{
            background: 'rgba(10, 12, 22, 0.95)',
            border: '2px solid #ff2a20',
            borderRadius: '16px',
            padding: '36px',
            maxWidth: '550px',
            width: '100%',
            textAlign: 'center',
            boxShadow: '0 0 50px rgba(255, 42, 32, 0.3)'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>🛡️</div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: '900', color: '#ff2a20', margin: '0 0 10px 0' }}>
              SERA SUBSYSTEM RECOVERY GATEWAY
            </h2>
            <p style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '20px', lineHeight: '1.6' }}>
              An isolated subsystem exception occurred. The SERA recovery system intercepted the error to protect workspace integrity.
            </p>

            <div className="mono" style={{
              background: '#000000',
              border: '1px solid rgba(255, 42, 32, 0.4)',
              color: '#ff5e3a',
              padding: '12px',
              borderRadius: '8px',
              fontSize: '11px',
              textAlign: 'left',
              marginBottom: '24px',
              overflowX: 'auto'
            }}>
              {this.state.error?.toString() || 'Unknown Subsystem Render Exception'}
            </div>

            <button
              onClick={this.handleReload}
              style={{
                background: 'linear-gradient(135deg, #ff2a20, #ff003c)',
                color: '#ffffff',
                border: 'none',
                borderRadius: '8px',
                padding: '12px 28px',
                fontSize: '13px',
                fontWeight: '900',
                cursor: 'pointer',
                boxShadow: '0 0 20px rgba(255, 42, 32, 0.5)'
              }}
            >
              🔄 REINITIALIZE SUBSYSTEM
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

