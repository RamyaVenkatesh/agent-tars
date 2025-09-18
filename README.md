# Agent Tars - Professional AI Assistant

A sophisticated AI-powered knowledge management system built with Claude API, featuring document search, calendar integration, and professional business automation capabilities.

## Features

- **Advanced Knowledge Search**: Semantic search across documents using FAISS vector indexing
- **Claude API Integration**: Powered by Anthropic's Claude for intelligent responses
- **Large Context Window**: Utilizes Claude's 200k token context for comprehensive understanding
- **Google Services**: Calendar and Gmail integration for business automation
- **Professional UI**: Clean, minimalist interface designed for business environments
- **Document Management**: Support for PDF, DOCX, TXT, and Markdown files
- **Enhanced Chunking**: Intelligent text segmentation optimized for large context windows

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

## Usage

### Chat Interface

The main chat interface supports various query types:

- **Knowledge Queries**: Ask about company policies, procedures, or documents
- **Calendar Queries**: Check schedules, meetings, and appointments
- **Analysis Requests**: Request analysis of documents or business information
- **Email Composition**: Draft and compose professional emails (coming soon)

### Document Management

- Upload documents through the web interface
- Supports PDF, DOCX, TXT, and Markdown formats
- Automatic text extraction and indexing
- Metadata tracking for better organization

### Professional Features

- Clean, business-appropriate interface
- Professional language and tone
- Comprehensive context understanding
- Actionable insights and recommendations

## Configuration

### Environment Variables

- `ANTHROPIC_API_KEY`: Your Claude API key (required)
- `STREAMLIT_SERVER_PORT`: Custom port for Streamlit (optional, default: 8501)

### Agent Configuration

Key settings in `ProfessionalKnowledgeAgent`:

- `chunk_size`: Document chunk size (default: 1200 characters)
- `overlap`: Chunk overlap for context continuity (default: 150 characters)
- `top_k`: Number of search results to consider (default: 10-15)
- `min_score`: Minimum similarity threshold (default: 0.2)
- `max_context_length`: Maximum context for Claude API (default: 180,000 tokens)

## Project Structure

```
agent-tars/
├── src/
│   └── agents/
│       └── claude_agent.py      # Main agent implementation
├── streamlit.py                 # Professional UI interface
├── requirements.txt             # Python dependencies
├── README.md                   # This file
├── knowledge.db                # SQLite database (created on first run)
├── credentials.json            # Google API credentials (optional)
└── token.pickle               # Google OAuth cache (created automatically)
```

## Development

### Extending the Agent

The `ProfessionalKnowledgeAgent` class is designed for extensibility:

- Add new intent types in `detect_user_intent()`
- Implement handlers for new functionality
- Customize prompts in system prompt variables
- Extend document processing for new file types

### UI Customization

The Streamlit interface uses custom CSS for professional styling:

- Modify styles in the `st.markdown()` CSS section
- Adjust color scheme through CSS variables
- Add new pages through the sidebar navigation

## Troubleshooting

### Common Issues

1. **Claude API Errors**: Verify your API key is set correctly
2. **Google Services**: Ensure credentials.json is in the root directory
3. **Document Processing**: Check file format support and file size limits
4. **Vector Search**: Rebuild index if search results seem inconsistent

### Performance Optimization

- Use larger chunk sizes for better context but fewer chunks
- Adjust `top_k` based on knowledge base size
- Monitor token usage for large conversations
- Consider batch document processing for large uploads

## License

This project is designed for professional business use. Ensure compliance with Anthropic's terms of service and Google API terms when deploying.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Claude API documentation
3. Verify Google API setup if using calendar/email features