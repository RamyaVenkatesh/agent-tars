# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with the Agent Tars repository.

## Project Evolution

Agent Tars represents the third generation in a series of AI agent development projects:

1. **Part 1**: Local Ollama-based agent with basic RAG functionality
2. **Part 2**: Enhanced local agent with Google Calendar/Gmail integration
3. **Part 3**: Agent Tars - Professional Claude API-powered system (current project)

This evolution demonstrates the transition from local LLM constraints to cloud-based AI capabilities, solving key challenges around context management, response quality, and professional deployment.

## Commands

### Development Commands
```bash
# Run the application
streamlit run streamlit.py

# Install dependencies
pip install -r requirements.txt

# Install in development mode (setuptools package)
pip install -e .

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Environment Setup
```bash
# Required environment variable
export ANTHROPIC_API_KEY="your-claude-api-key-here"

# Optional environment variables
export STREAMLIT_SERVER_PORT=8501
```

## Architecture Overview

### Core Components

**ProfessionalKnowledgeAgent** (`src/agents/claude_agent.py`)
- Main AI agent class powered by Claude API (claude-3-5-sonnet-20241022)
- Enhanced document chunking (1200 chars with 150 char overlap) using sentence-aware segmentation
- FAISS vector search with top-k=10-15 results (significantly improved from previous 3)
- Claude-powered intent detection routing queries to specialized handlers
- Four main intent handlers: KNOWLEDGE, CALENDAR, EMAIL, ANALYSIS
- Maintains comprehensive conversation context up to 180k tokens
- Integrated Google Calendar/Gmail APIs for business automation

**Streamlit Interface** (`streamlit.py`)
- Professional web UI with Nordic color scheme (#2E3440, #5E81AC, #ECEFF4)
- Three main pages: Chat (💬), Documents (📄), Knowledge Base (📊)
- Custom CSS removing Streamlit branding for professional deployment
- Multi-format file upload (PDF, DOCX, TXT, Markdown) with progress tracking
- Real-time system status indicators for Claude API, Google services, and knowledge base metrics
- Professional chat styling with user/assistant message bubbles

### Data Flow Architecture

1. **Document Processing**: Files → Text extraction → Enhanced chunking (sentence-aware, 1200 chars) → FAISS embedding
2. **Query Processing**: User input → Claude-powered intent detection → Route to specialized handler
3. **Knowledge Search**: Query → Vector similarity search (FAISS) → Top 10-15 results → Context enrichment
4. **Response Generation**: Search results + conversation history + system prompt → Claude API → Professional response

### Storage & Data Management
- **SQLite Database** (`knowledge.db`): Document storage with metadata, chunking info, timestamps
- **FAISS Index**: Vector embeddings for semantic search using SentenceTransformers ('all-MiniLM-L6-v2')
- **Google OAuth**: `token.pickle` for cached credentials, `credentials.json` for API setup
- **Conversation Context**: Enhanced tracking of recent searches and chat history (10 exchanges)

### Key Configuration Parameters
- `chunk_size`: 1200 characters (optimized for Claude's large context window)
- `overlap`: 150 characters for context continuity across chunks
- `top_k`: 10-15 search results (significantly enhanced from previous 3)
- `min_score`: 0.2 similarity threshold for relevant results
- `max_context_length`: 180,000 tokens (utilizing Claude's 200k context capacity)
- `model`: "claude-3-5-sonnet-20241022" (latest Claude version)

## Key Improvements Over Previous Versions

### From Local Ollama to Claude API
- **Performance**: Eliminated slow local LLM processing (~30+ seconds → ~2-3 seconds)
- **Context Window**: Expanded from 4k-8k tokens (Ollama) to 200k tokens (Claude)
- **Response Quality**: Professional, coherent responses vs. inconsistent local outputs
- **Reliability**: Cloud-based stability vs. local hardware constraints

### Enhanced Knowledge Management
- **Search Results**: Increased from 3 to 10-15 relevant documents per query
- **Chunking Strategy**: Improved from basic splitting to sentence-aware segmentation
- **Context Tracking**: Comprehensive conversation and search history management
- **Intent Detection**: AI-powered routing vs. keyword-based matching

### Professional Deployment Ready
- **UI Design**: Nordic color scheme, business-appropriate styling
- **Branding**: Removed Streamlit default elements for clean professional look
- **System Monitoring**: Real-time status indicators for all components
- **Scalability**: Designed for business environments with proper error handling

## Integration Points

### Google Services (Optional)
- **Calendar API**: Scope `https://www.googleapis.com/auth/calendar.readonly`
- **Gmail API**: Scope `https://www.googleapis.com/auth/gmail.compose` (enhanced functionality planned)
- Setup requires `credentials.json` in project root from Google Cloud Console
- OAuth token management with automatic refresh capability

### Document Processing Pipeline
- **Supported formats**: TXT, PDF (PyPDF2), DOCX (python-docx), Markdown
- **Enhanced chunking**: Sentence-aware splitting with configurable overlap
- **Metadata tracking**: File type, size, upload date, source information, relevance scores
- **Batch processing**: Support for multiple file uploads with progress tracking

## Development Notes

### Agent Architecture Enhancements
- **Intent Detection**: Claude-powered intelligent routing between four main handlers
- **Context Management**: Maintains conversation history and recent knowledge searches
- **Professional Prompts**: Business-appropriate system prompts for all interactions
- **Error Handling**: Graceful degradation with informative error messages

### Production Considerations
- **API Key Management**: Environment variable configuration for security
- **Database Schema**: Optimized SQLite structure with proper indexing
- **Vector Index**: FAISS optimization for fast similarity search
- **Memory Management**: Efficient handling of large document collections