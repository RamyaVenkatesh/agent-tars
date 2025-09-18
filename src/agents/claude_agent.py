import json
import sqlite3
import base64
import email.mime.text
import email.mime.multipart
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from datetime import datetime, timedelta
import os
import pickle
import re
from anthropic import Anthropic

# Google API imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class ProfessionalKnowledgeAgent:
    """
    Enhanced AI agent powered by Claude API with professional-grade capabilities
    for knowledge management, document search, and business automation.
    """

    def __init__(self, knowledge_db_path="knowledge.db", anthropic_api_key=None):
        # Claude API setup
        self.client = Anthropic(api_key=anthropic_api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-3-5-sonnet-20241022"  # Latest Claude model

        # Knowledge base setup with enhanced chunking
        self.db_path = knowledge_db_path
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.init_database()

        # Enhanced vector search setup
        self.vector_index = None
        self.document_chunks = []
        self.load_or_create_vector_index()

        # Google Services setup
        self.SCOPES = [
            'https://www.googleapis.com/auth/calendar.readonly',
            'https://www.googleapis.com/auth/gmail.compose'
        ]
        self.calendar_service = None
        self.gmail_service = None
        self.setup_google_services()

        # Enhanced conversation context tracking
        self.conversation_history = []
        self.recent_knowledge_searches = []
        self.max_context_length = 180000  # Utilize Claude's large context window

    def init_database(self):
        """Initialize SQLite database for enhanced document storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT,
                source TEXT,
                chunk_id INTEGER,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def add_document(self, title: str, content: str, source: str = "manual", metadata: Dict = None):
        """Add a document to the knowledge base with enhanced chunking"""
        # Enhanced chunking for larger context windows
        chunks = self.chunk_text(content, chunk_size=1200, overlap=150)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        metadata_json = json.dumps(metadata or {})

        for i, chunk in enumerate(chunks):
            cursor.execute('''
                INSERT INTO documents (title, content, source, chunk_id, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, chunk, source, i, metadata_json))

        conn.commit()
        conn.close()

        # Rebuild vector index after adding documents
        self.build_vector_index()
        print(f"✅ Document added: {title} ({len(chunks)} chunks)")

    def chunk_text(self, text: str, chunk_size: int = 1200, overlap: int = 150) -> List[str]:
        """Enhanced text chunking with better sentence preservation"""
        # Split by sentences first to maintain coherence
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            # If adding this sentence would exceed chunk_size, finalize current chunk
            if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                # Start new chunk with overlap from previous chunk
                words = current_chunk.split()
                overlap_words = words[-overlap//5:] if len(words) > overlap//5 else words
                current_chunk = " ".join(overlap_words) + " " + sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence

        # Add the last chunk if it exists
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    def build_vector_index(self):
        """Build FAISS vector index from documents"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, content FROM documents ORDER BY id')

        self.document_chunks = []
        embeddings = []

        for doc_id, content in cursor.fetchall():
            self.document_chunks.append((doc_id, content))
            embedding = self.embedding_model.encode(content)
            embeddings.append(embedding)

        conn.close()

        if embeddings:
            embeddings_array = np.array(embeddings).astype('float32')
            faiss.normalize_L2(embeddings_array)

            # Use IndexFlatIP for better similarity search
            self.vector_index = faiss.IndexFlatIP(embeddings_array.shape[1])
            self.vector_index.add(embeddings_array)
            print(f"📊 Vector index built with {len(embeddings)} embeddings")

    def load_or_create_vector_index(self):
        """Load existing vector index or create new one"""
        try:
            self.build_vector_index()
        except Exception as e:
            print(f"Creating new vector index: {e}")

    def search_knowledge_base(self, query: str, top_k: int = 10, min_score: float = 0.2) -> str:
        """Enhanced knowledge base search with larger result set"""
        if self.vector_index is None or len(self.document_chunks) == 0:
            return "Knowledge base is empty. Please add some documents first."

        query_embedding = self.embedding_model.encode([query])
        faiss.normalize_L2(query_embedding.astype('float32'))

        scores, indices = self.vector_index.search(query_embedding.astype('float32'), top_k)

        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.document_chunks) and score > min_score:
                doc_id, content = self.document_chunks[idx]

                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('SELECT title, source, metadata FROM documents WHERE id = ?', (doc_id,))
                metadata = cursor.fetchone()
                conn.close()

                if metadata:
                    title, source, metadata_json = metadata
                    results.append({
                        'content': content,
                        'title': title,
                        'source': source,
                        'metadata': json.loads(metadata_json or '{}'),
                        'relevance_score': float(score)
                    })

        if results:
            # Store for context in future queries
            search_info = {
                'query': query,
                'results': results,
                'timestamp': datetime.now()
            }
            self.recent_knowledge_searches.append(search_info)
            self.recent_knowledge_searches = self.recent_knowledge_searches[-10:]  # Keep more history

            formatted_results = "Relevant Information Found:\n\n"
            for i, result in enumerate(results, 1):
                formatted_results += f"Source {i}: {result['title']}\n"
                formatted_results += f"Content: {result['content']}\n"
                formatted_results += f"Relevance: {result['relevance_score']:.3f}\n\n"

            return formatted_results
        else:
            return "No relevant information found in the knowledge base."

    def setup_google_services(self):
        """Setup Google Calendar and Gmail services"""
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except:
                    creds = None

            if not creds and os.path.exists('credentials.json'):
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)

                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)

        if creds:
            try:
                self.calendar_service = build('calendar', 'v3', credentials=creds)
                self.gmail_service = build('gmail', 'v1', credentials=creds)
                print("✅ Google services connected")
            except Exception as e:
                print(f"❌ Google services setup failed: {e}")

    def get_calendar_events(self, days_ahead: int = 7) -> List[Dict]:
        """Get upcoming calendar events"""
        if not self.calendar_service:
            return []

        try:
            now = datetime.utcnow()
            time_max = now + timedelta(days=days_ahead)

            events_result = self.calendar_service.events().list(
                calendarId='primary',
                timeMin=now.isoformat() + 'Z',
                timeMax=time_max.isoformat() + 'Z',
                maxResults=20,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            return events_result.get('items', [])
        except Exception as e:
            print(f"Error fetching calendar events: {e}")
            return []

    def call_claude(self, messages: List[Dict[str, str]], system_prompt: str = None) -> str:
        """Enhanced Claude API call with conversation context"""
        try:
            kwargs = {
                "model": self.model,
                "max_tokens": 4096,
                "messages": messages
            }

            if system_prompt:
                kwargs["system"] = system_prompt

            response = self.client.messages.create(**kwargs)
            return response.content[0].text
        except Exception as e:
            return f"I apologize, but I encountered an error processing your request: {str(e)}"

    def build_conversation_context(self, chat_history: List = None) -> str:
        """Build comprehensive conversation context"""
        context_parts = []

        # Recent conversation history
        if chat_history:
            recent_history = chat_history[-10:]  # More history with larger context
            if recent_history:
                context_parts.append("Recent Conversation:")
                for role, message in recent_history:
                    context_parts.append(f"{role.title()}: {message}")
                context_parts.append("")

        # Recent knowledge searches
        if self.recent_knowledge_searches:
            context_parts.append("Recent Knowledge Base Searches:")
            for search in self.recent_knowledge_searches[-3:]:
                context_parts.append(f"Query: {search['query']}")
                context_parts.append(f"Found {len(search['results'])} relevant documents")
            context_parts.append("")

        return "\n".join(context_parts)

    def detect_user_intent(self, message: str, chat_history: List = None) -> str:
        """Enhanced intent detection using Claude"""
        context = self.build_conversation_context(chat_history)

        system_prompt = """You are an expert intent classification system for a professional business assistant.
        Analyze the user's message and conversation context to determine their primary intent.

        Return EXACTLY ONE of these intents:
        - CALENDAR: User wants to check calendar, schedule, appointments, meetings, or interviews
        - EMAIL: User wants to compose, send, or draft an email
        - KNOWLEDGE: User is asking questions about company information, policies, or documents
        - ANALYSIS: User wants analysis of candidates, documents, or business information

        Consider the full conversation context when making your decision."""

        messages = [
            {
                "role": "user",
                "content": f"{context}Current message: '{message}'\n\nWhat is the user's primary intent?"
            }
        ]

        response = self.call_claude(messages, system_prompt).strip().upper()

        if "CALENDAR" in response:
            return "CALENDAR"
        elif "EMAIL" in response:
            return "EMAIL"
        elif "ANALYSIS" in response:
            return "ANALYSIS"
        else:
            return "KNOWLEDGE"

    def chat(self, user_message: str, chat_history: List = None) -> str:
        """Enhanced main chat interface with comprehensive context"""
        try:
            # Detect user intent
            intent = self.detect_user_intent(user_message, chat_history)

            # Handle different intents
            if intent == "CALENDAR":
                return self.handle_calendar_query(user_message, chat_history)
            elif intent == "EMAIL":
                return self.handle_email_request(user_message, chat_history)
            elif intent == "ANALYSIS":
                return self.handle_analysis_request(user_message, chat_history)
            else:  # KNOWLEDGE
                return self.handle_knowledge_query(user_message, chat_history)

        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"

    def handle_knowledge_query(self, user_message: str, chat_history: List = None) -> str:
        """Handle knowledge base queries with enhanced context"""
        search_results = self.search_knowledge_base(user_message, top_k=12)
        context = self.build_conversation_context(chat_history)

        system_prompt = """You are a professional business assistant with access to a comprehensive knowledge base.
        Provide accurate, helpful, and well-structured responses based on the available information.

        Guidelines:
        - Be professional and concise
        - Cite specific sources when referencing information
        - If information is insufficient, acknowledge limitations
        - Provide actionable advice when appropriate
        - Maintain conversation continuity"""

        messages = [
            {
                "role": "user",
                "content": f"""{context}

User Question: {user_message}

Available Information:
{search_results}

Please provide a comprehensive, professional response based on the available information and conversation context."""
            }
        ]

        return self.call_claude(messages, system_prompt)

    def handle_calendar_query(self, user_message: str, chat_history: List = None) -> str:
        """Handle calendar-related queries"""
        if not self.calendar_service:
            return "Calendar integration is not available. Please configure Google Calendar access."

        # Extract time context
        days_ahead = self.extract_time_context(user_message)
        events = self.get_calendar_events(days_ahead)

        if not events:
            return f"No upcoming events found for the next {days_ahead} days."

        # Format events for Claude
        events_text = "Upcoming Events:\n\n"
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'No title')
            events_text += f"• {summary} - {start}\n"

        context = self.build_conversation_context(chat_history)

        system_prompt = """You are a professional scheduling assistant. Analyze the user's calendar query and provide helpful, organized information about their upcoming events. Be concise and actionable."""

        messages = [
            {
                "role": "user",
                "content": f"{context}\n\nUser Query: {user_message}\n\n{events_text}\n\nProvide a helpful response about their calendar."
            }
        ]

        return self.call_claude(messages, system_prompt)

    def handle_email_request(self, user_message: str, chat_history: List = None) -> str:
        """Handle email composition requests"""
        if not self.gmail_service:
            return "Gmail integration is not available. Please configure Google Gmail access."

        context = self.build_conversation_context(chat_history)

        # Determine if user wants to create a draft or send email
        is_draft_request = any(word in user_message.lower() for word in ['draft', 'drafts', 'save draft', 'create draft'])

        # Use Claude to extract email components and compose the email
        system_prompt = """You are a professional email assistant. Analyze the user's request and generate a well-structured email.

        Extract or infer:
        1. Recipient email address (if not provided, ask for it)
        2. Subject line
        3. Email body content

        Format your response as:
        TO: [email address or "MISSING - Please provide recipient email"]
        SUBJECT: [subject line]
        BODY:
        [email content]

        Make the email professional, clear, and appropriate for business communication."""

        messages = [
            {
                "role": "user",
                "content": f"{context}\n\nEmail Request: {user_message}\n\nPlease compose a professional email based on this request."
            }
        ]

        email_draft = self.call_claude(messages, system_prompt)

        # Parse the email components
        try:
            lines = email_draft.split('\n')
            to_email = None
            subject = None
            body_lines = []
            body_started = False

            for line in lines:
                if line.startswith('TO:'):
                    to_email = line.replace('TO:', '').strip()
                elif line.startswith('SUBJECT:'):
                    subject = line.replace('SUBJECT:', '').strip()
                elif line.startswith('BODY:'):
                    body_started = True
                elif body_started:
                    body_lines.append(line)

            body = '\n'.join(body_lines).strip()

            # For drafts, we can create without recipient; for sending, we need recipient
            if is_draft_request:
                # Create draft (can be without recipient)
                draft_to = to_email if to_email and "MISSING" not in to_email.upper() else ""
                result = self.create_email_draft(draft_to, subject, body)
                return result
            else:
                # For sending, recipient is required
                if not to_email or "MISSING" in to_email.upper():
                    return f"I've drafted your email, but I need the recipient's email address to send this email:\n\n**Subject:** {subject}\n\n**Body:**\n{body}\n\nPlease provide the recipient's email address to send this email."

                result = self.send_email(to_email, subject, body)
                return result

        except Exception as e:
            return f"I encountered an error while processing your email request: {str(e)}\n\nHere's the draft I prepared:\n\n{email_draft}"

    def handle_analysis_request(self, user_message: str, chat_history: List = None) -> str:
        """Handle analysis requests with knowledge base integration"""
        search_results = self.search_knowledge_base(user_message, top_k=15)
        context = self.build_conversation_context(chat_history)

        system_prompt = """You are a professional business analyst. Provide thorough, insightful analysis based on available information. Structure your analysis clearly with key findings, implications, and recommendations when appropriate."""

        messages = [
            {
                "role": "user",
                "content": f"""{context}

Analysis Request: {user_message}

Available Information:
{search_results}

Please provide a comprehensive analysis based on the available information."""
            }
        ]

        return self.call_claude(messages, system_prompt)

    def create_email_draft(self, to_email: str, subject: str, body: str) -> str:
        """Create email draft in Gmail"""
        if not self.gmail_service:
            return "Gmail service is not available. Please configure Google Gmail access."

        try:
            # Create the email message
            message = email.mime.text.MIMEText(body)
            if to_email:  # Only set 'to' field if email is provided
                message['to'] = to_email
            message['subject'] = subject

            # Encode the message
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

            # Create the draft
            draft_message = {'message': {'raw': raw}}
            result = self.gmail_service.users().drafts().create(
                userId="me",
                body=draft_message
            ).execute()

            to_display = f"**To:** {to_email}" if to_email else "**To:** (No recipient - you can add one in Gmail)"
            return f"✅ Draft created successfully in your Gmail!\n\n{to_display}\n**Subject:** {subject}\n\n**Draft ID:** {result.get('id', 'Unknown')}\n\nYou can find and edit this draft in your Gmail drafts folder."

        except HttpError as error:
            return f"❌ Failed to create draft: {error}"
        except Exception as e:
            return f"❌ An error occurred while creating the draft: {str(e)}"

    def send_email(self, to_email: str, subject: str, body: str) -> str:
        """Send email using Gmail API"""
        if not self.gmail_service:
            return "Gmail service is not available. Please configure Google Gmail access."

        try:
            # Create the email message
            message = email.mime.text.MIMEText(body)
            message['to'] = to_email
            message['subject'] = subject

            # Encode the message
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

            # Send the email
            send_message = {'raw': raw}
            result = self.gmail_service.users().messages().send(
                userId="me",
                body=send_message
            ).execute()

            return f"✅ Email sent successfully to {to_email}\n\n**Subject:** {subject}\n\n**Message ID:** {result.get('id', 'Unknown')}"

        except HttpError as error:
            return f"❌ Failed to send email: {error}"
        except Exception as e:
            return f"❌ An error occurred while sending the email: {str(e)}"

    def extract_time_context(self, message: str) -> int:
        """Extract time context from user message"""
        message_lower = message.lower()

        if any(word in message_lower for word in ['today', 'this morning', 'this afternoon']):
            return 1
        elif any(word in message_lower for word in ['tomorrow', 'next day']):
            return 2
        elif any(word in message_lower for word in ['this week', 'week']):
            return 7
        elif any(word in message_lower for word in ['next week']):
            return 14
        elif any(word in message_lower for word in ['month', 'this month']):
            return 30
        else:
            return 7  # Default to one week