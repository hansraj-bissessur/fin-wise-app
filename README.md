# FinWise - Financial Literacy Chatbot

An enterprise-grade Retrieval-Augmented Generation (RAG) chatbot for financial literacy education, built with FastAPI, Streamlit, LangChain, and Redis.

## 🌟 Features

- **📚 Document Management**: Upload and process PDF, DOCX, and XLSX financial documents
- **🤖 Intelligent Chat**: RAG-powered responses using Ollama (Phi3:mini) and semantic search
- **🔍 Vector Search**: Redis-backed vector store with efficient document retrieval
- **👨‍💼 Admin Portal**: Comprehensive document management interface
- **💬 User Interface**: Clean, intuitive chatbot interface for end users

## 🏗️ Architecture

FinWise follows a microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐
│  Admin Portal   │     │ Chatbot UI      │
│  (Streamlit)    │     │ (Streamlit)     │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     │
              ┌──────▼──────┐
              │   FastAPI   │
              │   Backend   │
              └──────┬──────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
    ┌────▼───┐  ┌───▼────┐ ┌───▼────┐
    │ Ollama │  │ Redis  │ │LangChain│
    │  LLM   │  │ Vector │ │  RAG   │
    └────────┘  └────────┘ └────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Redis 6.0 or higher
- Ollama with models:
  - `phi3:mini` (chat model)
  - `nomic-embed-text` (embeddings)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/hansraj-bissessur/fin-wise-app.git
cd finwise
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Start Redis**
```bash
redis-server
```

5. **Pull Ollama models**
```bash
ollama pull phi3:mini
ollama pull nomic-embed-text
```

### Running the Application

**Start the backend:**
```bash
# manually: uvicorn backend:app --reload --port 8000
```

**Start the admin portal:**
```bash
# manually: streamlit run admin_ui.py --server.port 8501
```

**Start the chatbot:**
```bash
# manually: streamlit run chatbot_ui.py --server.port 8502
```

Access the applications:
- Backend API: http://localhost:8000/docs
- Admin Portal: http://localhost:8501
- Chatbot: http://localhost:8502

## 📖 Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [API Documentation](docs/API_DOCUMENTATION.md)


## 🐳 Docker Deployment


This starts all services:
- Backend API (port 8000)
- Admin Portal (port 8501)
- Chatbot UI (port 8502)
- Redis (port 6379)
- Ollama (port 11434)

## 📦 Project Structure

```
fin-wise-app/
├── backend.py/
│   
├── admin_ui.py
│   
├── chatbot_ui.py
|
└── requirements.txt   
```

## 🛠️ Tech Stack

**Backend:**
- FastAPI - Modern Python web framework
- LangChain - RAG orchestration
- Redis - Vector database
- Ollama - Local LLM inference

**Frontend:**
- Streamlit - Rapid UI development

**Document Processing:**
- pypdf - PDF parsing
- python-docx - Word document parsing
- openpyxl - Excel parsing





