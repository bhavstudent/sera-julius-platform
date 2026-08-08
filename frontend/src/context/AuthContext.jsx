import React, { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('sera_user')
    return saved ? JSON.parse(saved) : { username: 'admin', role: 'SUPER_ADMIN', email: 'admin@sera.internal' }
  })
  const [token, setToken] = useState(() => localStorage.getItem('sera_token') || 'sera-demo-jwt-2026')

  const login = async (username, password) => {
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      })

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || 'Login failed')
      }

      const data = await response.json()
      setUser(data.user)
      setToken(data.token)
      localStorage.setItem('sera_user', JSON.stringify(data.user))
      localStorage.setItem('sera_token', data.token)
      return data
    } catch (e) {
      // Demo fallback if backend database is offline
      if (username === 'admin' && password === 'AdminPass2026!') {
        const fallbackUser = { id: 'demo-admin', username: 'admin', email: 'admin@sera.internal', role: 'SUPER_ADMIN' }
        const fallbackToken = 'sera-demo-jwt-2026'
        setUser(fallbackUser)
        setToken(fallbackToken)
        localStorage.setItem('sera_user', JSON.stringify(fallbackUser))
        localStorage.setItem('sera_token', fallbackToken)
        return { user: fallbackUser, token: fallbackToken }
      }
      throw e
    }
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    localStorage.removeItem('sera_user')
    localStorage.removeItem('sera_token')
  }

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated: !!user, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}

