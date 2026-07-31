const BASE = import.meta.env.VITE_API_BASE ?? ''
const API_KEY = import.meta.env.VITE_API_KEY ?? 'sera-demo-2026'

const AUTH_HEADERS = {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
}

// Helper function to handle API responses consistently
async function handleResponse(response, fallbackValue = null) {
    if (!response.ok) {
        console.warn(`[API] Request failed: ${response.status} ${response.statusText}`)
        return fallbackValue
    }
    try {
        return await response.json()
    } catch (e) {
        console.error('[API] Failed to parse JSON response:', e)
        return fallbackValue
    }
}

// Helper for POST requests
async function postRequest(endpoint, body = null) {
    try {
        const options = {
            method: 'POST',
            headers: AUTH_HEADERS
        }
        if (body) {
            options.body = JSON.stringify(body)
        }
        const response = await fetch(`${BASE}${endpoint}`, options)
        return await handleResponse(response, null)
    } catch (e) {
        console.error(`[API] POST ${endpoint} failed:`, e)
        return null
    }
}

// Helper for GET requests
async function getRequest(endpoint, fallbackValue = null) {
    try {
        const response = await fetch(`${BASE}${endpoint}`, { headers: AUTH_HEADERS })
        return await handleResponse(response, fallbackValue)
    } catch (e) {
        console.error(`[API] GET ${endpoint} failed:`, e)
        return fallbackValue
    }
}

// ============================================================
// DASHBOARD ENDPOINTS
// ============================================================

export async function fetchStats() {
    return getRequest('/api/dashboard/stats', null)
}

// ============================================================
// ENTITY ENDPOINTS
// ============================================================

export async function fetchEntities({ limit, offset } = {}) {
    const url = limit !== undefined 
        ? `/api/entities/?limit=${limit}&offset=${offset ?? 0}` 
        : '/api/entities/'
    return getRequest(url, null)
}

export async function globalSearchEntities(q) {
    return getRequest(`/api/entities/global-search?q=${encodeURIComponent(q)}`, null)
}

export async function fetchEntityFullProfile(ticker) {
    return getRequest(`/api/entities/${ticker}/full`, null)
}

// ============================================================
// AXIOM ENDPOINTS
// ============================================================

export async function fetchEntropy() {
    const data = await getRequest('/api/axiom/entropy', [])
    return Array.isArray(data) ? data : []
}

export async function fetchAlerts() {
    const data = await getRequest('/api/axiom/alerts', [])
    return Array.isArray(data) ? data : []
}

export async function fetchAxiomMonitor() {
    return getRequest('/api/axiom/monitor', null)
}

// ============================================================
// ZOLA / KRONOS ENDPOINTS
// ============================================================

export async function fetchPredictions() {
    const data = await getRequest('/api/zola/predictions', [])
    return Array.isArray(data) ? data : []
}

export async function fetchZolaDashboard() {
    return getRequest('/api/zola/dashboard', null)
}

export async function fetchZolaStatus() {
    return getRequest('/api/zola/status', null)
}

export async function triggerCyberspaceLearning() {
    return postRequest('/api/zola/learn')
}

export async function proposeSelfEvolution() {
    return postRequest('/api/zola/evolve/propose')
}

export async function validateSelfEvolution(patchId) {
    return postRequest(`/api/zola/evolve/validate/${patchId}`)
}

export async function approveSelfEvolution(patchId) {
    return postRequest(`/api/zola/evolve/approve/${patchId}`)
}

export async function runKronosOptimize() {
    return postRequest('/api/zola/kronos/optimize')
}

export async function fetchKronosStatus() {
    return getRequest('/api/zola/kronos/status', null)
}

export async function fetchEntityArchitecture() {
    return getRequest('/api/zola/entity/architecture', null)
}

export async function fetchAxiomAnalysis() {
    return getRequest('/api/zola/axiom/analysis', null)
}

export async function triggerKronosScaling() {
    return postRequest('/api/zola/kronos/scale')
}

export async function getScalingStatus() {
    return getRequest('/api/zola/kronos/scale/status', null)
}

export async function runAxiomCompression() {
    return postRequest('/api/zola/axiom/compress')
}

export async function getGodelAutoStatus() {
    return getRequest('/api/zola/godel/auto/status', null)
}

// ============================================================
// CHAT ENDPOINTS
// ============================================================

export async function sendChat(message) {
    try {
        const response = await fetch(`${BASE}/api/chat/`, {
            method: 'POST',
            headers: AUTH_HEADERS,
            body: JSON.stringify({ message })
        })
        if (!response.ok) {
            return { response: 'AI assistant is currently offline.' }
        }
        return await response.json()
    } catch (e) {
        console.error('sendChat failed:', e)
        return { response: 'Connection error. Is the backend running?' }
    }
}

// ============================================================
// NEWS & INTEL ENDPOINTS
// ============================================================

export async function fetchNews(domain = '') {
    const url = domain ? `/api/intel/news?domain=${domain}` : '/api/intel/news'
    const data = await getRequest(url, [])
    return Array.isArray(data) ? data : []
}

export async function fetchClassified() {
    const data = await getRequest('/api/intel/classified', [])
    return Array.isArray(data) ? data : []
}

export async function fetchDarkIntel() {
    return fetchClassified()
}

// ============================================================
// SIGNAL SYNTHESIS ENDPOINTS
// ============================================================

export async function fetchSynthesizedSignals(entityId) {
    return getRequest(`/api/synthesize/${entityId}`, null)
}

// ============================================================
// GRAPH / RELATIONSHIP ENDPOINTS
// ============================================================

export async function createRelationship({ source_entity_id, target_entity_id, relationship_type, confidence_score }) {
    return postRequest('/api/graph/relationship', {
        source_entity_id,
        target_entity_id,
        relationship_type,
        confidence_score
    })
}

export async function fetchEntityConnections(entityId, minConfidence = 0.0) {
    return getRequest(`/api/graph/entity/${entityId}/connections?min_confidence=${minConfidence}`, null)
}

export async function fetchEntityMultihop(entityId, depth = 2, minConfidence = 0.0) {
    return getRequest(
        `/api/graph/entity/${entityId}/multihop?depth=${depth}&min_confidence=${minConfidence}`,
        null
    )
}

// ============================================================
// CLAIMS / ALETHEIA ENDPOINTS
// ============================================================

export async function submitClaim({ claimant_id, content, stake_amount }) {
    return postRequest('/api/claims', { claimant_id, content, stake_amount })
}

export async function submitChallenge(claimId, { challenger_id, counter_stake_amount }) {
    return postRequest(`/api/claims/${claimId}/challenge`, { challenger_id, counter_stake_amount })
}

export async function reaffirmClaim(claimId) {
    return postRequest(`/api/claims/${claimId}/reaffirm`)
}

export async function fetchClaim(claimId) {
    return getRequest(`/api/claims/${claimId}`, null)
}

// ============================================================
// CITATION / GEO ENDPOINTS
// ============================================================

export async function fetchTrackedQueries() {
    return getRequest('/api/citation/tracked', null)
}

export async function addTrackedQuery({ query_text, target_entity_name }) {
    return postRequest('/api/citation/track', {
        query_text,
        target_entity_id: '',
        target_entity_name
    })
}

export async function runCitationCheck(queryId) {
    return postRequest(`/api/citation/run/${queryId}`)
}

export async function fetchQueryHistory(queryId) {
    const all = await getRequest('/api/citation/tracked', [])
    return Array.isArray(all) ? all.filter(q => q.id === queryId) : null
}

export async function fetchEntityCitationRate(entityName) {
    return getRequest(`/api/citation/rate?entity_name=${encodeURIComponent(entityName)}`, null)
}

// ============================================================
// HEALTH ENDPOINTS
// ============================================================

export async function fetchFreshness() {
    return getRequest('/api/health/freshness', null)
}

// ============================================================
// INSIGHTS ENDPOINTS
// ============================================================

export async function fetchNarrativeExpansion(ticker) {
    return getRequest(`/api/insights/narrative/expansion/${ticker}`, null)
}

// ============================================================
// HEALTHCARE ENDPOINTS
// ============================================================

export async function fetchHealthcareMetrics() {
    const data = await getRequest('/api/healthcare/metrics', [])
    return Array.isArray(data) ? data : []
}

// ============================================================
// EXECUTIVE ENDPOINTS
// ============================================================

export async function fetchExecutiveMovements() {
    const data = await getRequest('/api/executive/movements', { movements: [], last_7_days_count: 0 })
    return data || { movements: [], last_7_days_count: 0 }
}