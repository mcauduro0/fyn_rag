import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Search, Loader2, TrendingUp, AlertTriangle, Lightbulb, Brain, ChevronDown } from 'lucide-react'
import { performAnalysis, AnalysisRequest, AnalysisResponse } from '../lib/api'

export default function Analysis() {
  const [ticker, setTicker] = useState('')
  const [query, setQuery] = useState('')
  const [analysisDepth, setAnalysisDepth] = useState<'quick' | 'standard' | 'deep'>('standard')
  const [includeSentiment, setIncludeSentiment] = useState(true)
  const [includeForensics, setIncludeForensics] = useState(true)

  const analysisMutation = useMutation({
    mutationFn: (request: AnalysisRequest) => performAnalysis(request),
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!ticker && !query) return

    const analysisQuery = query || `Provide comprehensive investment analysis for ${ticker.toUpperCase()}. Include valuation, growth prospects, risks, and a clear recommendation.`

    analysisMutation.mutate({
      query: analysisQuery,
      ticker: ticker.toUpperCase() || undefined,
      analysis_depth: analysisDepth,
      include_sentiment: includeSentiment,
      include_forensics: includeForensics,
    })
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="heading-1">Investment Analysis</h1>
        <p className="text-fyn-text-dim mt-2">
          Analyze stocks using AI-powered multi-agent investment committee
        </p>
      </div>

      {/* Analysis Form */}
      <form onSubmit={handleSubmit} className="card-accent">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Ticker Input */}
          <div>
            <label className="block text-sm text-fyn-text-dim mb-2 uppercase">
              Stock Ticker
            </label>
            <input
              type="text"
              value={ticker}
              onChange={(e) => setTicker(e.target.value.toUpperCase())}
              placeholder="AAPL, MSFT, GOOGL..."
              className="input"
            />
          </div>

          {/* Analysis Depth */}
          <div>
            <label className="block text-sm text-fyn-text-dim mb-2 uppercase">
              Analysis Depth
            </label>
            <div className="relative">
              <select
                value={analysisDepth}
                onChange={(e) => setAnalysisDepth(e.target.value as 'quick' | 'standard' | 'deep')}
                className="input appearance-none cursor-pointer"
              >
                <option value="quick">Quick (2-3 min)</option>
                <option value="standard">Standard (5-7 min)</option>
                <option value="deep">Deep (10-15 min)</option>
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-fyn-text-dim" />
            </div>
          </div>

          {/* Submit */}
          <div className="flex items-end">
            <button
              type="submit"
              disabled={analysisMutation.isPending || (!ticker && !query)}
              className="btn btn-primary w-full flex items-center justify-center gap-2"
            >
              {analysisMutation.isPending ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Search className="w-5 h-5" />
                  Analyze
                </>
              )}
            </button>
          </div>
        </div>

        {/* Custom Query */}
        <div className="mt-6">
          <label className="block text-sm text-fyn-text-dim mb-2 uppercase">
            Custom Query (Optional)
          </label>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a specific question about the stock or investment opportunity..."
            rows={3}
            className="input resize-none"
          />
        </div>

        {/* Options */}
        <div className="mt-6 flex flex-wrap gap-6">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={includeSentiment}
              onChange={(e) => setIncludeSentiment(e.target.checked)}
              className="w-4 h-4 accent-fyn-accent"
            />
            <span className="text-sm">Include Reddit Sentiment</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={includeForensics}
              onChange={(e) => setIncludeForensics(e.target.checked)}
              className="w-4 h-4 accent-fyn-accent"
            />
            <span className="text-sm">Include Financial Forensics</span>
          </label>
        </div>
      </form>

      {/* Analysis Results */}
      {analysisMutation.data && (
        <AnalysisResults result={analysisMutation.data} />
      )}

      {/* Error */}
      {analysisMutation.error && (
        <div className="card border-fyn-danger">
          <div className="flex items-center gap-3 text-fyn-danger">
            <AlertTriangle className="w-5 h-5" />
            <span>Analysis failed. Please try again.</span>
          </div>
        </div>
      )}
    </div>
  )
}

function AnalysisResults({ result }: { result: AnalysisResponse }) {
  const getRecommendationColor = (rec?: string) => {
    if (!rec) return 'text-fyn-text-dim'
    if (rec.includes('BUY')) return 'text-fyn-accent'
    if (rec.includes('SELL')) return 'text-fyn-danger'
    return 'text-fyn-warning'
  }

  return (
    <div className="space-y-6">
      {/* Summary Card */}
      <div className="card-accent">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="heading-2">
              {result.ticker ? `${result.ticker} Analysis` : 'Analysis Complete'}
            </h2>
            <p className="text-sm text-fyn-text-dim mt-1">
              Completed in {result.execution_time_seconds?.toFixed(1)}s using {result.model}
            </p>
          </div>
          <div className="text-right">
            <p className={`text-3xl font-bold ${getRecommendationColor(result.recommendation)}`}>
              {result.recommendation || 'PENDING'}
            </p>
            {result.confidence && (
              <p className="text-sm text-fyn-text-dim">
                Confidence: {(result.confidence * 100).toFixed(0)}%
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Main Analysis */}
      <div className="card">
        <h3 className="heading-3 flex items-center gap-2 mb-4">
          <Brain className="w-5 h-5 text-fyn-accent" />
          Analysis
        </h3>
        <div className="prose prose-invert max-w-none">
          <pre className="whitespace-pre-wrap text-sm font-mono bg-fyn-bg p-4 border border-fyn-border overflow-x-auto">
            {result.analysis || 'No analysis available'}
          </pre>
        </div>
      </div>

      {/* Frameworks Used */}
      {result.frameworks_used && result.frameworks_used.length > 0 && (
        <div className="card">
          <h3 className="heading-3 flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-fyn-accent" />
            Frameworks Applied
          </h3>
          <div className="flex flex-wrap gap-2">
            {result.frameworks_used.map((fw, i) => (
              <span key={i} className="status-badge status-success">
                {fw}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Concerns & Opportunities */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {result.concerns && result.concerns.length > 0 && (
          <div className="card border-fyn-danger">
            <h3 className="heading-3 flex items-center gap-2 mb-4 text-fyn-danger">
              <AlertTriangle className="w-5 h-5" />
              Key Concerns
            </h3>
            <ul className="space-y-2">
              {result.concerns.map((concern, i) => (
                <li key={i} className="text-sm text-fyn-text-dim flex items-start gap-2">
                  <span className="text-fyn-danger">•</span>
                  {concern}
                </li>
              ))}
            </ul>
          </div>
        )}

        {result.opportunities && result.opportunities.length > 0 && (
          <div className="card border-fyn-accent">
            <h3 className="heading-3 flex items-center gap-2 mb-4 text-fyn-accent">
              <Lightbulb className="w-5 h-5" />
              Key Opportunities
            </h3>
            <ul className="space-y-2">
              {result.opportunities.map((opp, i) => (
                <li key={i} className="text-sm text-fyn-text-dim flex items-start gap-2">
                  <span className="text-fyn-accent">•</span>
                  {opp}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Tool Results */}
      {result.tool_results && result.tool_results.length > 0 && (
        <div className="card">
          <h3 className="heading-3 mb-4">Tools Used ({result.tool_results.length})</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {result.tool_results.map((tool, i) => (
              <div key={i} className="status-badge status-success">
                {tool.tool_name}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
