/**
 * api/guardian.ts
 * Guardian API — revenue, node metrics, network health helpers
 * used by GuardianDashboard.tsx
 */

const BASE = ''

function hdr(): Record<string, string> {
  const h: Record<string, string> = { 'Content-Type': 'application/json' }
  const t = localStorage.getItem('julius_token') || localStorage.getItem('sera_token')
  if (t) h['Authorization'] = `Bearer ${t}`
  return h
}

async function get<T = unknown>(url: string): Promise<T> {
  const r = await fetch(`${BASE}${url}`, { headers: hdr() })
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`)
  return (await r.json()) as T
}

// ── Revenue ────────────────────────────────────────────────────────────────────

export interface RevenueSummary {
  total_revenue_usd: number
  operations_tracked: string[]
  period_days?: number
}

export interface RevenueTrend {
  labels: string[]
  values: number[]
}

export async function getRevenueSummary(): Promise<RevenueSummary> {
  try {
    return await get<RevenueSummary>('/api/veil/revenue/summary')
  } catch {
    // graceful fallback with mock data so panel renders even if backend is offline
    return { total_revenue_usd: 0, operations_tracked: [], period_days: 30 }
  }
}

export async function getRevenueTrend(): Promise<RevenueTrend> {
  try {
    return await get<RevenueTrend>('/api/veil/revenue/trend')
  } catch {
    return { labels: [], values: [] }
  }
}

// ── Node Metrics ───────────────────────────────────────────────────────────────

export interface NodeMetrics {
  controlled_nodes: number
  active_nodes: number
  offline_nodes: number
  nodes: Record<string, unknown>[]
}

export async function getNodeMetrics(): Promise<NodeMetrics> {
  try {
    return await get<NodeMetrics>('/api/veil/nodes/metrics')
  } catch {
    return { controlled_nodes: 0, active_nodes: 0, offline_nodes: 0, nodes: [] }
  }
}

// ── Network Health ─────────────────────────────────────────────────────────────

export interface NetworkHealth {
  status: string
  latency_ms: number
  uptime_pct: number
  alerts: unknown[]
}

export interface NetworkMetrics {
  throughput_mbps: number
  packet_loss_pct: number
  active_connections: number
  suspicious_ips: string[]
}

export async function getNetworkHealth(): Promise<NetworkHealth> {
  try {
    return await get<NetworkHealth>('/api/monitoring/status')
  } catch {
    return { status: 'unknown', latency_ms: 0, uptime_pct: 0, alerts: [] }
  }
}

export async function getNetworkMetrics(): Promise<NetworkMetrics> {
  try {
    return await get<NetworkMetrics>('/api/network/metrics')
  } catch {
    return { throughput_mbps: 0, packet_loss_pct: 0, active_connections: 0, suspicious_ips: [] }
  }
}

// ── Transactions ───────────────────────────────────────────────────────────────

export interface Transaction {
  id: string
  amount: number
  currency: string
  status: string
  timestamp: string
  source?: string
  destination?: string
}

export async function getTransactions(limit = 50): Promise<Transaction[]> {
  try {
    return await get<Transaction[]>(`/api/veil/transactions?limit=${limit}`)
  } catch {
    return []
  }
}

// ── Alerts ─────────────────────────────────────────────────────────────────────

export interface Alert {
  id: string
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info'
  title: string
  message: string
  timestamp: string
  closed?: boolean
}

export async function getAlerts(limit = 100): Promise<Alert[]> {
  try {
    return await get<Alert[]>(`/api/guardian/alerts?limit=${limit}`)
  } catch {
    return []
  }
}

export async function closeAlert(alertId: string): Promise<{ success: boolean }> {
  try {
    const r = await fetch(`${BASE}/api/guardian/alerts/${alertId}/close`, {
      method: 'POST', headers: hdr(),
    })
    if (!r.ok) throw new Error(`${r.status}`)
    return await r.json() as { success: boolean }
  } catch {
    return { success: false }
  }
}
