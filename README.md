#  RAG-based Document Q&A (Hybrid RAG with Metrics)

This repository contains a production‑ready Retrieval‑Augmented Generation (RAG) system with a React (Vite + TypeScript + Tailwind) frontend and a FastAPI backend. It supports PDF upload, hybrid retrieval (vector + BM25) with lightweight intent‑aware re‑ranking, citation highlighting, multilingual queries, and a full metrics/benchmarking suite.

## Key Features

- Document upload and parsing (PDF → chunks → embeddings)
- Hybrid retrieval: vector search + BM25, optional re‑rank
- Faithful answers with inline citations and source preview
- Multilingual question handling (normalize/translate → cite original spans)
- Metrics and reports: Recall@5, Faithfulness, p95 latency, load test
- API docs (OpenAPI) and Postman collection under `API Docs/`

## Architecture

- Frontend: `frontend/` (Vite + React + TS), runs on http://localhost:3001
- Backend: `backend/app` (FastAPI + MongoDB + sentence‑transformers)
- Database: MongoDB (local via Docker or external Atlas)

![Architecture Diagram](./Architecture%20diagram.png)

---

## Quick Start (Docker)

1. Create a `.env` in the project root (Docker Compose reads it):
   ```env
   MONGODB_URL=mongodb://mongo:27017
   MONGODB_DATABASE=ragdb
   MONGODB_COLLECTION=documents
   MONGODB_VECTOR_INDEX=vector_index
   OPENAI_API_KEY=
   OPENROUTER_API_KEY=
   OPENROUTER_MODEL=
   APP_NAME=rag-app
   DEBUG=false
   HOST=0.0.0.0
   PORT=8000
   CORS_ORIGINS=*
   VECTOR_DIMENSION=384
   VECTOR_SEARCH_TOP_K=5
   EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
   EMBEDDING_DIMENSION=384
   ```

2. Build and run containers:
   ```bash
   docker compose build
   docker compose up -d
   ```

3. Verify services:
   - Backend health: `curl http://localhost:8000/health`
   - API docs: http://localhost:8000/docs
   - Frontend: http://localhost:3001

---

## Manual Setup (without Docker)

### Backend
1. Create a virtual env and install deps:
   ```bash
   cd backend
   python -m venv venv
   # Windows: .\venv\Scripts\activate | macOS/Linux: source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Configure environment:
   - Copy `env.example` → `.env` and fill MongoDB URL and API keys as needed.
3. Start API:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

### Frontend
```bash
cd frontend
npm install
npm run dev -- --port 3001
```
Open http://localhost:3001

---

## Using the API

Upload a PDF, list documents, search, and chat:
```bash
# Upload (replace with your path)
curl -F "file=@C:/path/to/resume.pdf" http://localhost:8000/api/v1/documents/upload

# List documents → copy a document_id
curl http://localhost:8000/api/v1/documents/list

# Search chunks (preview retrieval)
curl "http://localhost:8000/api/v1/document-chat/search?query=CGPA&document_id=<DOC_ID>&top_k=10"

# Chat (answers + citations)
curl -X POST http://localhost:8000/api/v1/document-chat/chat \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"What is the CGPA?\",\"course_id\":\"<DOC_ID>\",\"top_k\":10}"
```

---

## Metrics & Benchmarking

Two suites are included in the repo root:

- Quick enhanced metrics (prints Recall@5, Faithfulness, p95; with debug):
  ```bash
  python test_rag_metrics_improved.py
  ```

- Comprehensive benchmark (iterations, load test, plots, JSON report):
  ```bash
  python rag_benchmark.py
  ```

Outputs:
- JSON report: `rag_benchmark_report_*.json`
- Optional plots: `rag_benchmark_plots_*.png`
- Detailed CSV (from basic tester): `complete_rag_metrics_results_*.csv`

Recommended thresholds for production readiness:
- Recall@5 ≥ 0.75 on a ≥50‑question gold set
- Faithfulness ≥ 0.9 (answers directly supported by cited spans)
- p95 latency ≤ 2.5s (server‑side)

### Ablations
You can compare retrieval strategies by toggling envs and re‑running the benchmark:
- Vector‑only: `BM25_ENABLED=false`, `RERANK_ENABLED=false`
- Hybrid (vector + BM25): `BM25_ENABLED=true`, `RERANK_ENABLED=false`
- Hybrid + re‑rank (default): `BM25_ENABLED=true`, `RERANK_ENABLED=true`

Update env in `.env`, then:
```bash
docker compose restart backend
python rag_benchmark.py
```

---

## Troubleshooting

- Backend container build fails on Debian mirrors: we pin to bookworm and switch APT to HTTPS. If your network still blocks mirrors, build on a different network or remove `libmagic1` install and switch to `python-magic` only.
- Frontend not reachable: ensure port 3001 is free; `netstat -ano | findstr :3001` on Windows.
- Zero Recall/Faithfulness: confirm documents are uploaded and you pass the correct `document_id`. Use `/api/v1/documents/list` to verify.

---

## Project Layout

- `backend/app` — FastAPI app, services, endpoints
- `frontend/` — React UI
- `API Docs/` — OpenAPI spec and Postman collection
- `rag_benchmark.py`, `test_rag_metrics_improved.py` — metrics suites
- `docker-compose.yml`, `backend/Dockerfile`, `frontend/Dockerfile` — containerization

