import { useQuery } from '@tanstack/react-query'
import { TrendingUp, Brain, Shield, BarChart3, AlertTriangle, CheckCircle } from 'lucide-react'
import { getRAGStats, getAvailableTools, getAvailableFrameworks } from '../lib/api'

function MetricCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend
}: {
  title: string
  value: string | number
  subtitle?: string
  icon: React.ElementType
  trend?: 'up' | 'down' | 'neutral'
}) {
  return (
    <div className="card">
      <div className="flex items-start justify-between">
        <div>
          <p className="metric-label">{title}</p>
          <p className="metric-value mt-2">{value}</p>
          {subtitle && (
            <p className="text-sm text-fyn-text-dim mt-1">{subtitle}</p>
          )}
        </div>
        <div className="w-12 h-12 bg-fyn-accent/10 border border-fyn-accent flex items-center justify-center">
          <Icon className="w-6 h-6 text-fyn-accent" />
        </div>
      </div>
    </div>
  )
}

function AgentCard({ name, status, specialty }: { name: string; status: 'online' | 'busy'; specialty: string }) {
  return (
    <div className="card-accent flex items-center justify-between">
      <div>
        <h4 className="font-semibold">{name}</h4>
        <p className="text-sm text-fyn-text-dim">{specialty}</p>
      </div>
      <div className={`status-badge ${status === 'online' ? 'status-success' : 'status-warning'}`}>
        {status}
      </div>
    </div>
  )
}

export default function Dashboard() {
  const { data: frameworks } = useQuery({
    queryKey: ['frameworks'],
    queryFn: getAvailableFrameworks,
  })

  const { data: tools } = useQuery({
    queryKey: ['tools'],
    queryFn: getAvailableTools,
  })

  const agents = [
    { name: 'Value Investing Agent', status: 'online' as const, specialty: 'DCF, Moat Analysis, Buffett Methodology' },
    { name: 'Growth & VC Agent', status: 'online' as const, specialty: 'Rule of 40, TAM/SAM/SOM, Unit Economics' },
    { name: 'Risk Management Agent', status: 'online' as const, specialty: 'VaR, Stress Testing, Volatility' },
    { name: 'Industry & Competitive Agent', status: 'online' as const, specialty: "Porter's 5 Forces, SWOT, Market Share" },
    { name: 'Financial Forensics Agent', status: 'online' as const, specialty: 'M-Score, Z-Score, Quality of Earnings' },
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="heading-1">Investment Committee Dashboard</h1>
        <p className="text-fyn-text-dim mt-2">
          AI-powered investment analysis with multi-agent architecture
        </p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Investment Frameworks"
          value={frameworks?.total_frameworks || 138}
          subtitle="From legendary investors"
          icon={Brain}
        />
        <MetricCard
          title="Analysis Tools"
          value={tools?.total_tools || 15}
          subtitle="Advanced tool use enabled"
          icon={BarChart3}
        />
        <MetricCard
          title="Active Agents"
          value="5"
          subtitle="Value, Growth, Risk, Industry, Forensics"
          icon={Shield}
        />
        <MetricCard
          title="Today's Analyses"
          value="0"
          subtitle="Ready to analyze"
          icon={TrendingUp}
        />
      </div>

      {/* Agents Status */}
      <div>
        <h2 className="heading-2 mb-4">Investment Committee Agents</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.map((agent) => (
            <AgentCard key={agent.name} {...agent} />
          ))}
        </div>
      </div>

      {/* Framework Categories */}
      <div>
        <h2 className="heading-2 mb-4">Framework Categories</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {frameworks?.categories?.map((cat: { name: string; description: string; framework_count: number }) => (
            <div key={cat.name} className="card">
              <h4 className="font-semibold text-fyn-accent">{cat.name}</h4>
              <p className="text-2xl font-bold mt-2">{cat.framework_count}</p>
              <p className="text-xs text-fyn-text-dim mt-1">{cat.description}</p>
            </div>
          )) || (
            <>
              <div className="card">
                <h4 className="font-semibold text-fyn-accent">Value Investing</h4>
                <p className="text-2xl font-bold mt-2">35</p>
                <p className="text-xs text-fyn-text-dim mt-1">Buffett, Graham, Munger</p>
              </div>
              <div className="card">
                <h4 className="font-semibold text-fyn-accent">Growth & VC</h4>
                <p className="text-2xl font-bold mt-2">28</p>
                <p className="text-xs text-fyn-text-dim mt-1">Growth investing</p>
              </div>
              <div className="card">
                <h4 className="font-semibold text-fyn-accent">Risk Management</h4>
                <p className="text-2xl font-bold mt-2">25</p>
                <p className="text-xs text-fyn-text-dim mt-1">Risk assessment</p>
              </div>
              <div className="card">
                <h4 className="font-semibold text-fyn-accent">Industry Analysis</h4>
                <p className="text-2xl font-bold mt-2">30</p>
                <p className="text-xs text-fyn-text-dim mt-1">Competitive analysis</p>
              </div>
              <div className="card">
                <h4 className="font-semibold text-fyn-accent">Forensics</h4>
                <p className="text-2xl font-bold mt-2">20</p>
                <p className="text-xs text-fyn-text-dim mt-1">Earnings quality</p>
              </div>
            </>
          )}
        </div>
      </div>

      {/* System Status */}
      <div className="card">
        <h2 className="heading-3 mb-4">System Capabilities</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-center gap-3">
            <CheckCircle className="w-5 h-5 text-fyn-accent" />
            <span>Claude Advanced Tool Use (Anthropic)</span>
          </div>
          <div className="flex items-center gap-3">
            <CheckCircle className="w-5 h-5 text-fyn-accent" />
            <span>Real-time Market Data Integration</span>
          </div>
          <div className="flex items-center gap-3">
            <CheckCircle className="w-5 h-5 text-fyn-accent" />
            <span>138 Investment Frameworks (RAG)</span>
          </div>
          <div className="flex items-center gap-3">
            <CheckCircle className="w-5 h-5 text-fyn-accent" />
            <span>Reddit Sentiment Analysis</span>
          </div>
          <div className="flex items-center gap-3">
            <CheckCircle className="w-5 h-5 text-fyn-accent" />
            <span>Economic Data (FRED, Trading Economics)</span>
          </div>
          <div className="flex items-center gap-3">
            <CheckCircle className="w-5 h-5 text-fyn-accent" />
            <span>Multi-Agent Debate Simulation</span>
          </div>
        </div>
      </div>
    </div>
  )
}
