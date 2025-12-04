# Fyn RAG - Virtual Investment Committee System

AI-powered Investment Analysis System with Multi-Agent Architecture and RAG-based Knowledge Retrieval.

## 🎯 Overview

Fyn RAG is an institutional-grade investment analysis platform that combines:
- **200+ Investment Frameworks** via RAG (Retrieval-Augmented Generation)
- **Multi-Agent Architecture** with specialized investment analysts
- **Real-time Market Data** from Polygon.io, FMP, FRED, Trading Economics
- **Document Intelligence** for analyzing pitch decks, memos, and financial statements
- **Social Sentiment Analysis** from Reddit and other sources

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React + TS)                    │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                   FastAPI Backend                            │
├──────────────────────────────────────────────────────────────┤
│  ┌────────────┐  ┌──────────────┐  ┌──────────────────┐    │
│  │ RAG System │  │ Orchestrator │  │ Specialized      │    │
│  │ (FAISS)    │──│    Agent     │──│ Agents (5)       │    │
│  └────────────┘  └──────────────┘  └──────────────────┘    │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Data Layer: Polygon, FMP, FRED, Trading Economics,   │ │
│  │  Reddit, Document Processors (PDF, DOCX, XLSX)        │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│              PostgreSQL + FAISS Index                        │
└──────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- API Keys (see `.env.example`)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/mcauduro0/fyn_rag.git
cd fyn_rag
```

2. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Start with Docker Compose:**
```bash
docker-compose up -d
```

4. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📚 Sprint 1 - Foundation (Completed)

### ✅ Implemented Features

1. **RAG System**
   - Semantic chunking of 200 investment frameworks
   - FAISS indexing with sentence-transformers embeddings
   - Two-stage retrieval (FAISS + CrossEncoder reranking)
   - Query API with filtering by category and chunk type

2. **Data Fetchers**
   - Polygon.io: Real-time market data and historical prices
   - FMP: Comprehensive fundamental data (financials, ratios, growth)
   - FRED: Federal Reserve economic indicators
   - Trading Economics: Global economic data
   - Reddit: Sentiment analysis from r/wallstreetbets

3. **Document Processors**
   - PDF extraction with metadata
   - DOCX parsing with table support
   - XLSX spreadsheet analysis
   - Unified document processor interface

4. **API Endpoints**
   - `/api/v1/rag/query` - Query knowledge base
   - `/api/v1/rag/stats` - System statistics
   - `/api/v1/data/market/*` - Market data endpoints
   - `/api/v1/data/economic/*` - Economic data endpoints
   - `/api/v1/data/sentiment/*` - Sentiment analysis
   - `/api/v1/data/document/*` - Document processing

## 🧪 Testing

```bash
# Run all tests
cd backend
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run only fast tests (skip slow embedding tests)
pytest -m "not slow"

# Run integration tests (requires API keys)
pytest --run-integration
```

## 📖 API Documentation

### RAG Query Example

```bash
curl -X POST "http://localhost:8000/api/v1/rag/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How to evaluate a company competitive advantage?",
    "top_k": 5,
    "min_score": 0.5
  }'
```

### Market Data Example

```bash
curl -X POST "http://localhost:8000/api/v1/data/market/polygon" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'
```

### Document Processing Example

```bash
curl -X POST "http://localhost:8000/api/v1/data/document/process" \
  -F "file=@pitch_deck.pdf"
```

## 🗂️ Project Structure

```
fyn_rag/
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints and schemas
│   │   ├── core/             # Core business logic
│   │   │   └── rag/          # RAG system implementation
│   │   ├── data/             # Data fetchers and processors
│   │   │   ├── fetchers/     # External API integrations
│   │   │   └── processors/   # Document processors
│   │   └── main.py           # FastAPI application
│   ├── tests/                # Test suite
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                 # React frontend (Sprint 2)
├── data/
│   ├── faiss_index/         # FAISS index and metadata
│   └── uploads/             # Uploaded documents
├── docker-compose.yml
└── README.md
```

## 🔑 Environment Variables

Required API keys (see `.env.example`):

- `OPENAI_API_KEY` - OpenAI GPT models
- `ANTHROPIC_API_KEY` - Anthropic Claude models
- `POLYGON_API_KEY` - Polygon.io market data
- `FMP_API_KEY` - Financial Modeling Prep
- `FRED_API_KEY` - Federal Reserve economic data
- `TRADING_ECONOMICS_API_KEY` - Trading Economics
- `REDDIT_CLIENT_ID` - Reddit API
- `REDDIT_CLIENT_SECRET` - Reddit API

## 📈 Roadmap

### Sprint 2 (Weeks 3-4) - Agents & Orchestration
- [ ] Orchestrator Agent with task decomposition
- [ ] 5 Specialized Agents (Value, Growth, Risk, Industry, Forensics)
- [ ] Debate Simulator for consensus building
- [ ] Agent memory and context management

### Sprint 3 (Weeks 5-6) - Reports & Frontend
- [ ] Report generation engine
- [ ] Investment memo templates
- [ ] React frontend with real-time updates
- [ ] User authentication and authorization

## 🤝 Contributing

This is a private project. For questions or issues, contact the development team.

## 📄 License

Proprietary - All rights reserved

## 👥 Team

Developed by the Fyn team.

---

**Status:** Sprint 1 Complete ✅ | Next: Sprint 2 - Agents & Orchestration
