import { useState } from 'react'
import { Clock, TrendingUp, Search, Filter } from 'lucide-react'

interface HistoryItem {
  id: string
  ticker: string
  query: string
  recommendation: string
  confidence: number
  timestamp: string
}

// Mock data for now - will be replaced with real API calls
const mockHistory: HistoryItem[] = []

export default function History() {
  const [searchTerm, setSearchTerm] = useState('')
  const [filterRec, setFilterRec] = useState<string>('all')

  const filteredHistory = mockHistory.filter(item => {
    const matchesSearch = item.ticker.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.query.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesFilter = filterRec === 'all' || item.recommendation === filterRec
    return matchesSearch && matchesFilter
  })

  const getRecColor = (rec: string) => {
    if (rec.includes('BUY')) return 'text-fyn-accent'
    if (rec.includes('SELL')) return 'text-fyn-danger'
    return 'text-fyn-warning'
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="heading-1">Analysis History</h1>
        <p className="text-fyn-text-dim mt-2">
          View past analyses and track investment decisions
        </p>
      </div>

      {/* Filters */}
      <div className="card flex flex-wrap items-center gap-4">
        <div className="flex-1 min-w-[200px]">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-fyn-text-dim" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by ticker or query..."
              className="input pl-10"
            />
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Filter className="w-5 h-5 text-fyn-text-dim" />
          <select
            value={filterRec}
            onChange={(e) => setFilterRec(e.target.value)}
            className="input w-auto"
          >
            <option value="all">All Recommendations</option>
            <option value="BUY">BUY</option>
            <option value="HOLD">HOLD</option>
            <option value="SELL">SELL</option>
          </select>
        </div>
      </div>

      {/* History Table */}
      {filteredHistory.length > 0 ? (
        <div className="card overflow-hidden p-0">
          <table className="w-full">
            <thead>
              <tr className="table-header">
                <th className="text-left p-4">Ticker</th>
                <th className="text-left p-4">Query</th>
                <th className="text-left p-4">Recommendation</th>
                <th className="text-left p-4">Confidence</th>
                <th className="text-left p-4">Date</th>
              </tr>
            </thead>
            <tbody>
              {filteredHistory.map((item) => (
                <tr key={item.id} className="table-row">
                  <td className="p-4 font-semibold text-fyn-accent">{item.ticker}</td>
                  <td className="p-4 max-w-xs truncate">{item.query}</td>
                  <td className={`p-4 font-semibold ${getRecColor(item.recommendation)}`}>
                    {item.recommendation}
                  </td>
                  <td className="p-4">{(item.confidence * 100).toFixed(0)}%</td>
                  <td className="p-4 text-fyn-text-dim">
                    {new Date(item.timestamp).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="card text-center py-16">
          <Clock className="w-16 h-16 text-fyn-border mx-auto mb-4" />
          <h3 className="heading-3 text-fyn-text-dim">No Analysis History</h3>
          <p className="text-sm text-fyn-text-dim mt-2">
            Your completed analyses will appear here
          </p>
          <a
            href="/analysis"
            className="btn btn-primary inline-flex items-center gap-2 mt-6"
          >
            <TrendingUp className="w-5 h-5" />
            Start First Analysis
          </a>
        </div>
      )}
    </div>
  )
}
