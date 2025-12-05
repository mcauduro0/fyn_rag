import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Save, RefreshCw, Database, Brain, Globe, MessageSquare } from 'lucide-react'
import { healthCheck, getAvailableTools } from '../lib/api'

export default function Settings() {
  const [defaultDepth, setDefaultDepth] = useState('standard')
  const [defaultSentiment, setDefaultSentiment] = useState(true)
  const [defaultForensics, setDefaultForensics] = useState(true)
  const [llmProvider, setLlmProvider] = useState('anthropic')

  const { data: health, refetch: refetchHealth } = useQuery({
    queryKey: ['health'],
    queryFn: healthCheck,
  })

  const { data: tools } = useQuery({
    queryKey: ['tools'],
    queryFn: getAvailableTools,
  })

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="heading-1">Settings</h1>
        <p className="text-fyn-text-dim mt-2">
          Configure analysis preferences and system settings
        </p>
      </div>

      {/* System Status */}
      <div className="card-accent">
        <div className="flex items-center justify-between mb-6">
          <h2 className="heading-2">System Status</h2>
          <button
            onClick={() => refetchHealth()}
            className="btn btn-secondary flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="flex items-center gap-4">
            <div className={`w-3 h-3 rounded-full ${health?.status === 'healthy' ? 'bg-fyn-accent' : 'bg-fyn-danger'}`} />
            <div>
              <p className="text-sm text-fyn-text-dim">API Status</p>
              <p className="font-semibold">{health?.status || 'Checking...'}</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <Database className="w-5 h-5 text-fyn-accent" />
            <div>
              <p className="text-sm text-fyn-text-dim">Database</p>
              <p className="font-semibold">{health?.database || 'Unknown'}</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <Brain className="w-5 h-5 text-fyn-accent" />
            <div>
              <p className="text-sm text-fyn-text-dim">RAG System</p>
              <p className="font-semibold">{health?.rag_system || 'Unknown'}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Analysis Defaults */}
      <div className="card">
        <h2 className="heading-2 mb-6">Analysis Defaults</h2>
        <div className="space-y-6">
          <div>
            <label className="block text-sm text-fyn-text-dim mb-2 uppercase">
              Default Analysis Depth
            </label>
            <select
              value={defaultDepth}
              onChange={(e) => setDefaultDepth(e.target.value)}
              className="input max-w-xs"
            >
              <option value="quick">Quick (2-3 min)</option>
              <option value="standard">Standard (5-7 min)</option>
              <option value="deep">Deep (10-15 min)</option>
            </select>
          </div>

          <div className="flex flex-wrap gap-6">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={defaultSentiment}
                onChange={(e) => setDefaultSentiment(e.target.checked)}
                className="w-5 h-5 accent-fyn-accent"
              />
              <div>
                <p className="font-medium">Reddit Sentiment Analysis</p>
                <p className="text-sm text-fyn-text-dim">Include r/wallstreetbets analysis</p>
              </div>
            </label>

            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={defaultForensics}
                onChange={(e) => setDefaultForensics(e.target.checked)}
                className="w-5 h-5 accent-fyn-accent"
              />
              <div>
                <p className="font-medium">Financial Forensics</p>
                <p className="text-sm text-fyn-text-dim">Include M-Score, Z-Score analysis</p>
              </div>
            </label>
          </div>
        </div>
      </div>

      {/* LLM Configuration */}
      <div className="card">
        <h2 className="heading-2 mb-6">LLM Configuration</h2>
        <div className="space-y-6">
          <div>
            <label className="block text-sm text-fyn-text-dim mb-2 uppercase">
              Primary LLM Provider
            </label>
            <select
              value={llmProvider}
              onChange={(e) => setLlmProvider(e.target.value)}
              className="input max-w-xs"
            >
              <option value="anthropic">Anthropic (Claude Sonnet 4.5)</option>
              <option value="openai">OpenAI (GPT-4 Turbo)</option>
            </select>
            <p className="text-sm text-fyn-text-dim mt-2">
              Claude is recommended for Advanced Tool Use capabilities
            </p>
          </div>
        </div>
      </div>

      {/* Available Tools */}
      <div className="card">
        <h2 className="heading-2 mb-6">Available Analysis Tools ({tools?.total_tools || 0})</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {tools?.tools?.map((tool: { name: string; description: string }) => (
            <div key={tool.name} className="p-4 bg-fyn-bg border border-fyn-border">
              <p className="font-semibold text-fyn-accent text-sm">{tool.name}</p>
              <p className="text-xs text-fyn-text-dim mt-1 line-clamp-2">{tool.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* API Integrations */}
      <div className="card">
        <h2 className="heading-2 mb-6">API Integrations</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-center gap-4 p-4 bg-fyn-bg border border-fyn-border">
            <Globe className="w-8 h-8 text-fyn-accent" />
            <div>
              <p className="font-semibold">FRED API</p>
              <p className="text-sm text-fyn-text-dim">Federal Reserve Economic Data</p>
            </div>
            <div className="ml-auto status-badge status-success">Connected</div>
          </div>
          <div className="flex items-center gap-4 p-4 bg-fyn-bg border border-fyn-border">
            <Globe className="w-8 h-8 text-fyn-accent" />
            <div>
              <p className="font-semibold">Trading Economics</p>
              <p className="text-sm text-fyn-text-dim">Global Economic Indicators</p>
            </div>
            <div className="ml-auto status-badge status-success">Connected</div>
          </div>
          <div className="flex items-center gap-4 p-4 bg-fyn-bg border border-fyn-border">
            <MessageSquare className="w-8 h-8 text-fyn-accent" />
            <div>
              <p className="font-semibold">Reddit API</p>
              <p className="text-sm text-fyn-text-dim">Sentiment from r/wallstreetbets</p>
            </div>
            <div className="ml-auto status-badge status-success">Connected</div>
          </div>
          <div className="flex items-center gap-4 p-4 bg-fyn-bg border border-fyn-border">
            <Brain className="w-8 h-8 text-fyn-accent" />
            <div>
              <p className="font-semibold">Anthropic API</p>
              <p className="text-sm text-fyn-text-dim">Claude Advanced Tool Use</p>
            </div>
            <div className="ml-auto status-badge status-success">Connected</div>
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <button className="btn btn-primary flex items-center gap-2">
          <Save className="w-5 h-5" />
          Save Settings
        </button>
      </div>
    </div>
  )
}
