# FinWise Architecture Documentation

## Overview

This document describes the system architecture, design decisions, and component interactions.

## System Architecture

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Presentation Layer                     │
│  ┌─────────────────────┐    ┌──────────────────────┐    │
│  │   Admin Portal      │    │   Chatbot UI         │    │
│  │   (Streamlit)       │    │   (Streamlit)        │    │
│  └──────────┬──────────┘    └──────────┬───────────┘    │
└─────────────┼─────────────────────────┼─────────────────┘
              │                          │
              │      HTTP/REST API       │
              │                          │
┌─────────────▼──────────────────────────▼─────────────────┐
│                    Application Layer                      │
│  ┌────────────────────────────────────────────────────┐  │
│  │              FastAPI Backend                       │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────┐ │  │
│  │  │ Admin API    │  │  Chat API    │  │ Health  │ │  │
│  │  │ /api/v1/admin│  │ /api/v1/chat │  │ /health │ │  │
│  │  └──────┬───────┘  └──────┬───────┘  └────┬────┘ │  │
│  │         │                 │                │      │  │
│  │  ┌──────▼─────────────────▼────────────────▼────┐ │  │
│  │  │           Service Layer                       │ │  │
│  │  │  ┌──────────────────┐  ┌──────────────────┐  │ │  │
│  │  │  │ Document Service │  │  Chat Service    │  │ │  │
│  │  │  └────────┬─────────┘  └────────┬─────────┘  │ │  │
│  │  └───────────┼──────────────────────┼───────────┘ │  │
│  └──────────────┼──────────────────────┼─────────────┘  │
└─────────────────┼──────────────────────┼─────────────────┘
                  │                      │
┌─────────────────▼──────────────────────▼─────────────────┐
│                    Core Layer                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────┐ │
│  │ Document         │  │  RAG Engine      │  │ Vector │ │
│  │ Processor        │  │  (LangChain)     │  │ Store  │ │
│  └──────────────────┘  └──────────────────┘  └────────┘ │
└───────────────────────────────────────────────────────────┘
                  │                      │
┌─────────────────▼──────────────────────▼─────────────────┐
│                 Infrastructure Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Ollama     │  │    Redis     │  │  File System │   │
│  │   (LLM)      │  │  (VectorDB)  │  │              │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└───────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Presentation Layer

#### Admin Portal (Streamlit)
- **Purpose**: Document management interface for administrators
- **Features**:
  - Multi-file document upload (PDF, DOCX, XLSX)
  - Document history tracking
  - System health monitoring
  - Vector store management (clear all documents)
- **Technology**: Streamlit with component-based architecture

#### Chatbot UI (Streamlit)
- **Purpose**: End-user interface for financial literacy queries
- **Features**:
  - Real-time chat interface
  - Message history management
  - Typing indicators
  - Error handling and retry logic
- **Technology**: Streamlit with session state management

### 2. Application Layer

#### FastAPI Backend

**API Structure:**
```
/api/v1/
├── admin/
│   ├── POST /documents/upload         # Upload documents
│   └── DELETE /documents/clear        # Clear all documents
├── chat/
│   └── POST /                         # Process chat queries
└── /health                            # Health check endpoint
```

**Key Components:**

### 1. Core Layer

#### Document Processor

**Text Extraction Pipeline:**
```
File Upload → Parser Selection → Text Extraction → 
Validation → Text Splitting → Metadata Enrichment
```

**Parsers:**
- **PDF Parser**: pypdf - Extracts text from PDF documents
- **DOCX Parser**: python-docx - Processes Word documents
- **XLSX Parser**: openpyxl - Extracts data from Excel sheets

**Text Splitting:**
- Algorithm: RecursiveCharacterTextSplitter
- Chunk Size: 1000 characters
- Overlap: 200 characters
- Preserves context across chunks

**Metadata Schema:**
```json
{
  "fileName": "financial_guide.pdf",
  "fileType": "application/pdf",
  "userId": "admin123",
  "chunkIndex": 0,
  "totalChunks": 45,
  "category": "financial_literacy",
  "uploadTimestamp": "2025-10-24T10:30:00"
}
```

#### RAG Engine

**Query Processing Flow:**
```
User Query → Embedding → Vector Search → 
Context Retrieval → Prompt Construction → 
LLM Inference → Response Generation
```

**Components:**

1. **Embedding Model**
   - Model: `nomic-embed-text` via Ollama
   - Dimension: 768
   - Purpose: Convert text to semantic vectors

2. **Retriever**
   - Strategy: Similarity search
   - Top K: 3 documents
   - Distance Metric: Cosine similarity

3. **Prompt Template**
```python
SYSTEM_PROMPT = """
You are a financial assistant. Provide concise, helpful 
answers using the context below. Keep responses under 
150 words for mobile users.

CONTEXT:
{documents}
"""
```

4. **LLM**
   - Model: `phi3:mini` via Ollama
   - Temperature: 0.7 (configurable)
   - Max Tokens: 512
   - Purpose: Generate natural language responses

5. **Confidence Scoring**
```python
def calculate_confidence(relevant_docs):
    if not relevant_docs:
        return 0.2
    return min(1.0, 0.5 + (len(relevant_docs) / 3.0 * 0.5))
```

**Confidence Thresholds:**
- < 0.5: Suggest human support
- 0.5 - 0.75: Moderate confidence
- > 0.75: High confidence

#### Vector Store

**Redis Configuration:**
```python
REDIS_URL = "redis://localhost:6379"
INDEX_NAME = "financial_literacy_docs"
VECTOR_DIMENSIONS = 768
DISTANCE_METRIC = "COSINE"
```

**Index Schema:**
- Vector field: Embedded document chunks
- Metadata fields: fileName, fileType, userId, category
- Text field: Original chunk content

**Operations:**
- `add_documents()`: Batch insert with embeddings
- `similarity_search()`: Vector similarity query
- `delete_all()`: Index clearing

## Data Flow Diagrams

### Document Upload Flow

```
┌─────────┐
│  Admin  │
└────┬────┘
     │ 1. Upload Files
     ▼
┌─────────────────┐
│ Admin Portal    │
│ (Streamlit)     │
└────┬────────────┘
     │ 2. POST /api/v1/admin/documents/upload
     ▼
┌─────────────────┐
│  FastAPI API    │
│  Endpoint       │
└────┬────────────┘
     │ 3. Validate & Route
     ▼
┌─────────────────┐
│ Document        │
│ Service         │
└────┬────────────┘
     │ 4. Process each file
     ▼
┌─────────────────┐
│ Document        │
│ Processor       │
└────┬────────────┘
     │ 5. Parse → Split → Enrich
     ▼
┌─────────────────┐
│ Vector Store    │
│ (Redis)         │
└────┬────────────┘
     │ 6. Embed & Store
     ▼
┌─────────────────┐
│ Ollama          │
│ Embeddings      │
└─────────────────┘
```

### Chat Query Flow

```
┌─────────┐
│  User   │
└────┬────┘
     │ 1. Send Query
     ▼
┌─────────────────┐
│ Chatbot UI      │
│ (Streamlit)     │
└────┬────────────┘
     │ 2. POST /api/v1/chat
     ▼
┌─────────────────┐
│  FastAPI API    │
│  Endpoint       │
└────┬────────────┘
     │ 3. Route to Service
     ▼
┌─────────────────┐
│ Chat Service    │
└────┬────────────┘
     │ 4. Invoke RAG Pipeline
     ▼
┌─────────────────┐
│ RAG Engine      │
└────┬────────────┘
     │ 5. Retrieve Context
     ├─────────────────┐
     ▼                 ▼
┌──────────┐    ┌──────────┐
│ Vector   │    │ Ollama   │
│ Store    │    │ LLM      │
└──────┬───┘    └────┬─────┘
       │ 6. Docs    │ 7. Response
       └──────┬─────┘
              ▼
       ┌─────────────┐
       │Calculate    │
       │Confidence   │
       └──────┬──────┘
              │ 8. Format Response
              ▼
       ┌─────────────┐
       │ Return to   │
       │ User        │
       └─────────────┘
```


### 3. RAG Implementation

**Chunk Size: 1000 characters**
- Balances context vs precision
- Fits within embedding model limits
- Maintains coherent semantic units

**Overlap: 200 characters**
- Prevents information loss at boundaries
- Improves retrieval accuracy
- Handles sentences spanning chunks

**Top K: 3 documents**
- Provides sufficient context
- Keeps prompt size manageable
- Balances relevance vs diversity

**Confidence Scoring**
- Simple, interpretable algorithm
- Based on retrieval success
- Triggers human escalation appropriately


