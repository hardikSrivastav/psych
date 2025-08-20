# AI Psychologist RAG System - Technical Specification

## Overview
A minimal AI psychologist chatbot leveraging RAG (Retrieval-Augmented Generation) with psychology research papers to provide scientifically-grounded, empathetic responses. Built with FastAPI backend and React frontend, containerized with Docker.

## Technical Architecture

### Stack
- **Backend**: Python FastAPI
- **Vector Database**: Qdrant
- **Cache Layer**: Redis
- **LLM Provider**: OpenAI API
- **Frontend**: React/Next.js
- **Deployment**: Docker + docker-compose
- **Logging**: File-based logging to `/logs` directory

### System Components

#### Backend Services
- **FastAPI Application**: REST API server with chat endpoints
- **QdrantService**: Vector database operations for paper embeddings
- **RedisService**: Session management and conversation caching
- **OpenAIService**: Embedding generation and chat completion
- **RAGService**: Core retrieval-augmented generation pipeline
- **EvaluationService**: LLM-as-judge response scoring system

#### Data Pipeline
- **Paper Ingestion**: Academic database integration for psychology papers
- **Text Processing**: Section-based chunking (Abstract, Introduction, Methods, Results, Discussion)
- **Embedding Generation**: OpenAI text-embedding-3-large (3072 dimensions)
- **Vector Storage**: Qdrant collection with metadata filtering

## Detailed Specifications

### 1. Vector Database (Qdrant)

**Collection Configuration**:
- **Name**: `psychology_papers`
- **Vector Size**: 3072 (text-embedding-3-large)
- **Distance**: Cosine similarity
- **Single collection**: Unified storage with metadata filtering

**Payload Structure**:
```json
{
  "paper_id": "paper_uuid",
  "title": "Paper Title",
  "authors": ["Author1", "Author2"],
  "section_type": "results|discussion|introduction|abstract|methods",
  "therapeutic_modality": ["CBT", "DBT", "humanistic"],
  "journal": "Journal Name",
  "year": 2023,
  "doi": "10.xxxx/xxxxx",
  "text": "Section content text",
  "chunk_index": 0
}
```

**Retrieval Parameters**:
- **Chunks per query**: 5
- **Similarity threshold**: 0.75 minimum
- **Metadata filters**: Optional filtering by therapeutic modality, section type, year range

### 2. Session Management (Redis)

**Session Architecture**:
- **Session Creation**: Backend-generated UUID4 on first message
- **Storage Pattern**: `chat:{session_id}` → JSON array of messages
- **TTL**: 24 hours (86400 seconds)
- **Conversation Limit**: 10 messages (FIFO truncation)

**Message Schema**:
```json
{
  "role": "user|assistant",
  "content": "message content",
  "timestamp": "ISO 8601",
  "metadata": {
    "retrieved_chunks": 5,
    "similarity_scores": [0.85, 0.82, 0.79, 0.77, 0.75]
  }
}
```

**Redis Configuration**:
- **Memory Policy**: allkeys-lru
- **Max Memory**: 256MB
- **Persistence**: Disabled (ephemeral storage)

### 3. RAG Pipeline

**Query Processing Flow**:
1. **Input**: User message + session_id (optional)
2. **Session Retrieval**: Get last 10 messages from Redis
3. **Query Embedding**: Generate vector using OpenAI text-embedding-3-large
4. **Similarity Search**: Query Qdrant with 0.75 threshold, retrieve 5 chunks
5. **Context Assembly**: Combine retrieved chunks + conversation history
6. **Response Generation**: OpenAI GPT-4 with therapeutic system prompt
7. **Session Update**: Store new message in Redis with metadata

**System Prompt Framework**:
- Therapeutic guidelines (CBT, DBT, humanistic approaches)
- Safety constraints (no medical diagnosis, crisis protocols)
- Empathy and validation emphasis
- Scientific grounding requirements

### 4. API Endpoints

#### Core Chat Endpoint
```
POST /chat
Content-Type: application/json

Request:
{
  "message": "User input text",
  "session_id": "optional_uuid" // If null, creates new session
}

Response:
{
  "response": "AI psychologist response",
  "session_id": "session_uuid",
  "metadata": {
    "chunks_retrieved": 5,
    "response_time_ms": 1250,
    "tokens_used": 890
  }
}
```

#### Health & Monitoring
```
GET /health - Service health check
GET /metrics - Basic performance metrics
```

#### Evaluation Endpoints (Development)
```
POST /evaluate/compare - Compare RAG vs baseline responses
POST /evaluate/batch - Batch evaluation of test scenarios
```

### 5. Data Ingestion Pipeline

**Paper Collection**:
- Academic database integration (PubMed, PsycINFO, etc.)
- Target domains: Clinical psychology, CBT, DBT, humanistic therapy
- Quality filters: Peer-reviewed, recent publications (2015+)

**Text Processing**:
- PDF parsing and section extraction
- Section-based chunking preservation
- Metadata extraction (authors, journal, year, DOI)
- Duplicate detection and removal

**Embedding & Storage**:
- Batch processing for cost efficiency
- Error handling for failed embeddings
- Progress tracking and resumption capability

### 6. Evaluation System

**LLM-as-Judge Configuration**:
- **Model**: GPT-4 for evaluation consistency
- **Scoring Dimensions**:
  - Empathy (1-5): Warmth, understanding, validation
  - Scientific Accuracy (1-5): Therapeutic concept alignment
  - Safety (1-5): Harm avoidance, appropriate boundaries
  - Therapeutic Value (1-5): Promotes self-reflection, insight

**Test Dataset**:
- 20-30 standardized scenarios (anxiety, depression, relationships)
- Comparison against baseline GPT-4 responses
- Human validation sample for calibration

### 7. Project Structure

```
app/
├── api/
│   ├── __init__.py
│   ├── chat.py          # Chat endpoints
│   ├── health.py        # Health/monitoring
│   └── evaluation.py    # Evaluation endpoints
├── core/
│   ├── __init__.py
│   ├── config.py        # Environment configuration
│   └── rag.py          # RAG orchestration service
├── models/
│   ├── __init__.py
│   ├── chat.py         # Pydantic schemas
│   └── evaluation.py   # Evaluation schemas
├── services/
│   ├── __init__.py
│   ├── qdrant.py       # Vector database service
│   ├── redis.py        # Session management service
│   ├── openai.py       # LLM and embedding service
│   └── evaluation.py   # LLM-as-judge service
├── utils/
│   ├── __init__.py
│   ├── preprocessing.py # Text processing utilities
│   └── logging.py      # Logging configuration
├── data/
│   └── ingestion/      # Paper collection scripts
├── logs/               # Application logs
├── tests/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── main.py
```

### 8. Logging Configuration

**Log Structure**:
- **Location**: `/logs` directory within container
- **Files**:
  - `app.log`: General application logs
  - `chat.log`: Chat interactions and responses
  - `rag.log`: RAG pipeline operations
  - `evaluation.log`: Model evaluation results
  - `error.log`: Error and exception tracking

**Log Format**:
```
[TIMESTAMP] [LEVEL] [SERVICE] [SESSION_ID] MESSAGE
```

**Log Levels**:
- **INFO**: Normal operations, chat interactions
- **WARNING**: Performance issues, fallback usage
- **ERROR**: Failures, exceptions
- **DEBUG**: Detailed pipeline steps (development only)

**Log Rotation**:
- Daily rotation with 7-day retention
- Max file size: 100MB per file

### 9. Docker Configuration

**Multi-service Setup**:
- **FastAPI**: Application server on port 8000
- **Qdrant**: Vector database on port 6333
- **Redis**: Cache layer on port 6379

**Volume Mounts**:
- `./logs:/app/logs`: Persistent logging
- `./qdrant_data:/qdrant/storage`: Vector database persistence
- `./data:/app/data`: Paper ingestion data

**Environment Variables**:
```env
OPENAI_API_KEY=sk-xxxxx
QDRANT_URL=http://qdrant:6333
REDIS_URL=redis://redis:6379
LOG_LEVEL=INFO
SESSION_TTL_HOURS=24
MAX_CONVERSATION_LENGTH=10
```

### 10. Performance Requirements

**Response Times**:
- **Target**: < 2 seconds for chat responses
- **Maximum**: < 5 seconds for complex queries

**Throughput**:
- **Concurrent sessions**: 50+ simultaneous conversations
- **Daily conversations**: 1000+ chat interactions

**Resource Limits**:
- **Memory**: 2GB total (FastAPI: 1GB, Qdrant: 512MB, Redis: 256MB)
- **Storage**: 5GB for vector database + papers

### 11. Security & Privacy

**Data Handling**:
- No persistent conversation storage beyond 24 hours
- No user identification or tracking
- Automatic session cleanup

**API Security**:
- Rate limiting: 100 requests per minute per IP
- Input validation and sanitization
- CORS configuration for frontend domains

**Compliance**:
- HIPAA-aligned data handling practices
- No medical record generation or storage
- Clear disclaimers about AI limitations

### 12. Success Metrics

**Technical Performance**:
- RAG retrieval relevance > 70%
- Response time < 2 seconds (95th percentile)
- System uptime > 99%

**Quality Metrics**:
- Evaluation scores > baseline GPT-4 across all dimensions
- Zero harmful responses in test scenarios
- Scientific accuracy > 4/5 average rating

**User Experience**:
- Session completion rate > 80%
- Average conversation length > 5 exchanges
- Minimal error rates < 1%
