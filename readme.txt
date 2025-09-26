RAG-based Document Q&A (Hybrid RAG with Metrics)

This repository contains a production-ready Retrieval-Augmented Generation (RAG) system with a React (Vite + TypeScript + Tailwind) frontend and a FastAPI backend. It supports PDF upload, hybrid retrieval (vector + BM25) with lightweight intent-aware re-ranking, citation highlighting, multilingual queries, and a full metrics/benchmarking suite.

Key Features
- Document upload and parsing (PDF  > chunks  > embeddings)
- Hybrid retrieval: vector search + BM25, optional re-rank
- Faithful answers with inline citations and source preview
- Multilingual question handling (normalize/translate  > cite original spans)
- Metrics and reports: Recall@5, Faithfulness, p95 latency, load test
- API docs (OpenAPI) and Postman collection under `API Docs/`

Quick Start (Docker)
1) Create a .env in the project root (Compose reads it):
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

2) Build and run:
   docker compose build
   docker compose up -d

3) Verify:
   curl http://localhost:8000/health
   Frontend: http://localhost:3001
   API docs: http://localhost:8000/docs

Manual Setup (without Docker)
Backend
- cd backend
- python -m venv venv
- (Windows) .\\venv\\Scripts\\activate  |  (macOS/Linux) source venv/bin/activate
- pip install -r requirements.txt
- copy env.example  > .env and fill MongoDB URL + keys
- uvicorn app.main:app --host 0.0.0.0 --port 8000

Frontend
- cd frontend
- npm install
- npm run dev -- --port 3001

API Usage
- Upload:   curl -F "file=@C:/path/to/resume.pdf" http://localhost:8000/api/v1/documents/upload
- List:     curl http://localhost:8000/api/v1/documents/list
- Search:   curl "http://localhost:8000/api/v1/document-chat/search?query=CGPA&document_id=<DOC_ID>&top_k=10"
- Chat:     curl -X POST http://localhost:8000/api/v1/document-chat/chat -H "Content-Type: application/json" -d "{\"query\":\"What is the CGPA?\",\"course_id\":\"<DOC_ID>\",\"top_k\":10}"

Metrics & Benchmarking
- Quick enhanced metrics:
  python test_rag_metrics_improved.py
- Full benchmark with plots:
  python rag_benchmark.py

Targets
- Recall@5  > 0.75 on  >50-question gold set
- Faithfulness  > 0.9 (answers supported by cited spans)
- p95 latency  < 2.5s (server-side)

Ablations
- Vector-only: BM25_ENABLED=false, RERANK_ENABLED=false
- Hybrid: BM25_ENABLED=true, RERANK_ENABLED=false
- Hybrid + re-rank (default): BM25_ENABLED=true, RERANK_ENABLED=true

Troubleshooting
- Debian mirror build errors: use bookworm + HTTPS (already configured); if blocked, build on another network or remove libmagic install.
- Frontend port: ensure 3001 is free (Windows: netstat -ano | findstr :3001).
- Zero recall/faithfulness: verify documents uploaded and correct document_id via /api/v1/documents/list.
