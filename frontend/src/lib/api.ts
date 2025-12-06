import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Types
export interface AnalysisRequest {
  query: string
  ticker?: string
  asset_type?: 'listed' | 'illiquid'
  analysis_depth?: 'quick' | 'standard' | 'deep'
  include_sentiment?: boolean
  include_forensics?: boolean
  context?: Record<string, unknown>
}

export interface AnalysisResponse {
  success: boolean
  request_id: string
  query: string
  ticker?: string
  analysis?: string
  recommendation?: string
  confidence?: number
  tool_results?: Array<{
    tool_name: string
    result: unknown
  }>
  frameworks_used?: string[]
  concerns?: string[]
  opportunities?: string[]
  execution_time_seconds: number
  model: string
  timestamp: string
}

export interface HealthStatus {
  status: string
  database: string
  rag_system: string
}

export interface SystemMetrics {
  uptime: number
  total_requests: number
  error_rate: number
  avg_latency_ms: number
}

// API Functions
export const healthCheck = async (): Promise<HealthStatus> => {
  const response = await api.get('/monitoring/health')
  return response.data
}

export const getSystemMetrics = async (): Promise<SystemMetrics> => {
  const response = await api.get('/monitoring/metrics')
  return response.data
}

export const performAnalysis = async (request: AnalysisRequest): Promise<AnalysisResponse> => {
  const response = await api.post('/advanced-analysis/analyze', request)
  return response.data
}

export const quickAnalysis = async (ticker: string, question?: string) => {
  const response = await api.post('/advanced-analysis/quick-analysis', {
    ticker,
    question,
  })
  return response.data
}

export const compareStocks = async (tickers: string[], criteria?: string[]) => {
  const response = await api.post('/advanced-analysis/compare', {
    tickers,
    criteria: criteria || ['valuation', 'growth', 'risk', 'moat'],
  })
  return response.data
}

export const getAvailableFrameworks = async () => {
  const response = await api.get('/advanced-analysis/frameworks')
  return response.data
}

export const getAvailableTools = async () => {
  const response = await api.get('/advanced-analysis/tools')
  return response.data
}

export const queryRAG = async (query: string, options?: {
  top_k?: number
  min_score?: number
  categories?: string[]
}) => {
  const response = await api.post('/rag/query', {
    query,
    ...options,
  })
  return response.data
}

export const getRAGStats = async () => {
  const response = await api.get('/rag/stats')
  return response.data
}

// ============================================================================
// API HEALTH CHECK
// ============================================================================

export interface APIStatus {
  name: string
  status: 'connected' | 'error' | 'not_configured'
  latency_ms?: number
  last_checked: string
  error?: string
}

export interface APIHealthResponse {
  overall_status: 'healthy' | 'degraded' | 'unhealthy'
  apis: APIStatus[]
  timestamp: string
}

export interface APIConfiguration {
  apis: Record<string, {
    configured: boolean
    description: string
  }>
  timestamp: string
}

export const getAPIHealth = async (): Promise<APIHealthResponse> => {
  const response = await api.get('/api-health/status')
  return response.data
}

export const checkSingleAPI = async (apiName: string): Promise<APIStatus> => {
  const response = await api.get(`/api-health/status/${apiName}`)
  return response.data
}

export const getAPIConfiguration = async (): Promise<APIConfiguration> => {
  const response = await api.get('/api-health/configuration')
  return response.data
}

// ============================================================================
// MARKET DATA
// ============================================================================

export interface StockPrice {
  ticker: string
  price?: number
  change?: number
  change_percent?: number
  volume?: number
  market_cap?: number
  name?: string
}

export interface EconomicIndicator {
  series_id: string
  latest_value: number
  latest_date: string
  title?: string
}

export const getStockPrice = async (ticker: string): Promise<StockPrice> => {
  const result = await performAnalysis({
    query: `Get current stock price for ${ticker}`,
    ticker,
    analysis_depth: 'quick'
  })
  return result.tool_results?.find(t => t.tool_name === 'get_stock_price')?.result as StockPrice || { ticker }
}

export const getMarketOverview = async () => {
  const response = await api.get('/data/market-overview')
  return response.data
}

export const getEconomicIndicators = async (indicators: string[]): Promise<Record<string, EconomicIndicator>> => {
  const result = await performAnalysis({
    query: `Get economic indicators: ${indicators.join(', ')}`,
    analysis_depth: 'quick'
  })
  return result.tool_results?.find(t => t.tool_name === 'get_economic_indicators')?.result as Record<string, EconomicIndicator> || {}
}
