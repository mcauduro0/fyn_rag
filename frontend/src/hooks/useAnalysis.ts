import { useMutation, useQuery } from '@tanstack/react-query'
import { performAnalysis, quickAnalysis, compareStocks, AnalysisRequest } from '../lib/api'

export function usePerformAnalysis() {
  return useMutation({
    mutationFn: (request: AnalysisRequest) => performAnalysis(request),
  })
}

export function useQuickAnalysis() {
  return useMutation({
    mutationFn: ({ ticker, question }: { ticker: string; question?: string }) =>
      quickAnalysis(ticker, question),
  })
}

export function useCompareStocks() {
  return useMutation({
    mutationFn: ({ tickers, criteria }: { tickers: string[]; criteria?: string[] }) =>
      compareStocks(tickers, criteria),
  })
}
