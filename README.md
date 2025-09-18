# Agent Tars - Cloud-Based AI Personal Assistant

An AI-powered personal assistant and knowledge management system built with Claude API that can perform document search, calendar integration and email management
## Features

### Personal Assistant Capabilities
- **Calendar Management**: Check schedules, meetings, and appointments through natural language
- **Email Automation**: Draft, compose, and send emails via Gmail integration
- **Intelligent Intent Detection**: Automatically routes queries to appropriate handlers (knowledge, calendar, email, analysis)

### Knowledge Management
- **Advanced Document Search**: Semantic search across documents using FAISS vector indexing
- **Multi-Format Support**: PDF, DOCX, TXT, and Markdown file processing
- **Enhanced Chunking**: Intelligent text segmentation optimized for large context windows
- **Context-Aware Responses**: Maintains conversation history for coherent interactions

### Technical details
- **Claude API Integration**: Powered by Anthropic's Claude with 200k token context window
- **Google Services Integration**: Calendar and Gmail connectivity

## Quick Start

### Prerequisites

1. **Anthropic API Key**: Get your API key from [Anthropic Console](https://console.anthropic.com/)
2. **Python 3.8+**: Ensure you have Python installed
3. **Google Credentials** (optional): For calendar/email integration

### Installation

1. **Clone or create the project directory**:
   ```bash
   cd agent-tars
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   export ANTHROPIC_API_KEY="your-claude-api-key-here"
   ```

5. **Run the application**:
   ```bash
   streamlit run streamlit.py
   ```

### Google Services Setup (Optional)

For calendar and email integration:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Calendar API and Gmail API
4. Create OAuth 2.0 credentials (Desktop application)
5. Download `credentials.json` to the project root
6. Run the app - you'll be prompted to authenticate on first use

## Architecture

### Core Components

- **ProfessionalKnowledgeAgent**: Main agent class with Claude API integration
- **Enhanced Document Chunking**: 1200-character chunks with 150-character overlap
- **FAISS Vector Search**: Semantic similarity search with configurable thresholds
- **Context Management**: Comprehensive conversation history and knowledge tracking
- **Intent Detection**: Intelligent routing for different query types

### Data Flow

1. Documents are processed and chunked with sentence-aware segmentation
2. Text embeddings generated using SentenceTransformers
3. Vector index created with FAISS for fast similarity search
4. User queries trigger semantic search across document chunks
5. Context and search results sent to Claude API for response generation
6. Conversation history maintained for continuity

## Configuration

### Environment Variables

- `ANTHROPIC_API_KEY`: Your Claude API key (required)
- `STREAMLIT_SERVER_PORT`: Custom port for Streamlit (optional, default: 8501)

## Development

### Extending the Agent

The `ProfessionalKnowledgeAgent` class is designed for extensibility:

- Add new intent types in `detect_user_intent()`
- Implement handlers for new functionality
- Customize prompts in system prompt variables
- Extend document processing for new file types

### Performance Optimization

- Use larger chunk sizes for better context but fewer chunks
- Adjust `top_k` based on knowledge base size
- Monitor token usage for large conversations
- Consider batch document processing for large uploads

## License

This project is designed for professional business use. Ensure compliance with Anthropic's terms of service and Google API terms when deploying.
