import streamlit as st
import os
import sys
from pathlib import Path
import io
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from agents.claude_agent import ProfessionalKnowledgeAgent

# Optional imports for document processing
try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

try:
    import docx
    DOCX_SUPPORT = True
except ImportError:
    DOCX_SUPPORT = False

# Professional page configuration
st.set_page_config(
    page_title="Agent Tars - Professional AI Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional appearance
st.markdown("""
<style>
    /* Main container styling */
    .main {
        padding: 2rem 1rem;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Professional color scheme */
    :root {
        --primary-color: #2E3440;
        --secondary-color: #3B4252;
        --accent-color: #5E81AC;
        --background-color: #ECEFF4;
        --text-color: #2E3440;
        --border-color: #D8DEE9;
    }

    /* Chat message styling */
    .user-message {
        background: linear-gradient(135deg, #5E81AC, #81A1C1);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 1.5rem;
        margin: 0.5rem 0 0.5rem auto;
        max-width: 75%;
        box-shadow: 0 2px 8px rgba(94, 129, 172, 0.2);
    }

    .assistant-message {
        background: #F8F9FA;
        color: #2E3440;
        padding: 1rem 1.5rem;
        border-radius: 1.5rem;
        margin: 0.5rem auto 0.5rem 0;
        max-width: 85%;
        border-left: 4px solid #5E81AC;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }

    /* Professional sidebar styling */
    .css-1d391kg {
        background-color: #F8F9FA;
        border-right: 1px solid #D8DEE9;
    }

    /* Status indicators */
    .status-connected {
        background: #A3BE8C;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        margin: 0.25rem 0;
        text-align: center;
        font-weight: 500;
    }

    .status-warning {
        background: #EBCB8B;
        color: #2E3440;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        margin: 0.25rem 0;
        text-align: center;
        font-weight: 500;
    }

    .status-error {
        background: #BF616A;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        margin: 0.25rem 0;
        text-align: center;
        font-weight: 500;
    }

    /* Professional button styling */
    .stButton > button {
        background: #5E81AC;
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background: #4C688B;
        box-shadow: 0 4px 12px rgba(94, 129, 172, 0.3);
    }

    /* Input field styling */
    .stTextInput > div > div > input {
        border: 2px solid #D8DEE9;
        border-radius: 0.5rem;
        padding: 0.75rem;
        font-size: 1rem;
    }

    .stTextInput > div > div > input:focus {
        border-color: #5E81AC;
        box-shadow: 0 0 0 3px rgba(94, 129, 172, 0.1);
    }

    /* Welcome message styling */
    .welcome-message {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #F8F9FA, #ECEFF4);
        border-radius: 1rem;
        margin: 2rem 0;
        border: 1px solid #D8DEE9;
    }

    .welcome-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2E3440;
        margin-bottom: 1rem;
    }

    .welcome-subtitle {
        font-size: 1rem;
        color: #4C566A;
        line-height: 1.6;
    }

    /* Professional metrics */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #D8DEE9;
        margin: 0.5rem 0;
        text-align: center;
    }

    .metric-value {
        font-size: 1.5rem;
        font-weight: 600;
        color: #5E81AC;
    }

    .metric-label {
        font-size: 0.9rem;
        color: #4C566A;
        margin-top: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = ProfessionalKnowledgeAgent()

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def extract_text_from_uploaded_file(uploaded_file):
    """Extract text from uploaded files"""
    try:
        if uploaded_file.type == "text/plain":
            return str(uploaded_file.read(), "utf-8")

        elif uploaded_file.type == "application/pdf" and PDF_SUPPORT:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text

        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document" and DOCX_SUPPORT:
            doc = docx.Document(uploaded_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text

        else:
            st.error(f"Unsupported file type: {uploaded_file.type}")
            return None
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

def render_chat_message(role, message):
    """Render a chat message with professional styling"""
    if role == "user":
        st.markdown(f"""
            <div style="display: flex; justify-content: flex-end; margin: 1rem 0;">
                <div class="user-message">
                    {message}
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div style="display: flex; justify-content: flex-start; margin: 1rem 0;">
                <div class="assistant-message">
                    {message}
                </div>
            </div>
        """, unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
        <div style="text-align: center; padding: 1rem 0 2rem 0;">
            <h1 style="color: #2E3440; font-weight: 600; margin-bottom: 0.5rem;">
                Agent Tars
            </h1>
            <p style="color: #4C566A; font-size: 1.1rem; margin: 0;">
                Professional AI Assistant for Knowledge Management
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown("### Navigation")
        page = st.radio(
            "",
            ["💬 Chat", "📄 Documents", "📊 Knowledge Base"],
            label_visibility="collapsed"
        )

        st.markdown("---")
        st.markdown("### System Status")

        # Claude API status
        try:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                st.markdown('<div class="status-connected">Claude API Connected</div>',
                           unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-error">Claude API Key Required</div>',
                           unsafe_allow_html=True)
        except:
            st.markdown('<div class="status-error">Claude API Error</div>',
                       unsafe_allow_html=True)

        # Google Services status
        if st.session_state.agent.calendar_service:
            st.markdown('<div class="status-connected">Google Calendar Connected</div>',
                       unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-warning">Google Calendar Disconnected</div>',
                       unsafe_allow_html=True)

        # Knowledge base metrics
        try:
            import sqlite3
            conn = sqlite3.connect(st.session_state.agent.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(DISTINCT title) FROM documents")
            doc_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM documents")
            chunk_count = cursor.fetchone()[0]
            conn.close()

            st.markdown("### Knowledge Base")
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{doc_count}</div>
                    <div class="metric-label">Documents</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{chunk_count}</div>
                    <div class="metric-label">Chunks</div>
                </div>
            """, unsafe_allow_html=True)
        except:
            st.markdown("### Knowledge Base")
            st.markdown('<div class="metric-card"><div class="metric-label">No data available</div></div>',
                       unsafe_allow_html=True)

    # Main content area
    if page == "💬 Chat":
        # Chat interface
        chat_container = st.container()

        with chat_container:
            if st.session_state.chat_history:
                for role, message in st.session_state.chat_history:
                    render_chat_message(role, message)
            else:
                # Professional welcome message
                st.markdown("""
                    <div class="welcome-message">
                        <div class="welcome-title">Welcome to Agent Tars</div>
                        <div class="welcome-subtitle">
                            I'm your professional AI assistant, ready to help with knowledge queries,
                            calendar management, and document analysis. How may I assist you today?
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        # Chat input
        st.markdown("---")

        with st.form(key="chat_form", clear_on_submit=True):
            col1, col2 = st.columns([6, 1])

            with col1:
                user_input = st.text_input(
                    "",
                    placeholder="Ask about company information, calendar, or documents...",
                    label_visibility="collapsed"
                )

            with col2:
                send_button = st.form_submit_button("Send", use_container_width=True)

        if send_button and user_input.strip():
            # Add user message
            st.session_state.chat_history.append(("user", user_input.strip()))

            # Get response
            with st.spinner("Processing your request..."):
                try:
                    response = st.session_state.agent.chat(
                        user_input.strip(),
                        st.session_state.chat_history[:-1]
                    )
                    st.session_state.chat_history.append(("assistant", response))
                except Exception as e:
                    error_msg = f"I apologize, but I encountered an error: {str(e)}"
                    st.session_state.chat_history.append(("assistant", error_msg))

            st.rerun()

        # Clear chat option
        if st.session_state.chat_history:
            if st.sidebar.button("Clear Conversation", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()

    elif page == "📄 Documents":
        st.markdown("## Document Management")
        st.markdown("Upload and manage documents for your knowledge base.")

        # File uploader
        uploaded_files = st.file_uploader(
            "Select documents to upload",
            type=['txt', 'pdf', 'docx', 'md'],
            accept_multiple_files=True,
            help="Supported formats: TXT, PDF, DOCX, Markdown"
        )

        if uploaded_files:
            st.markdown("### Selected Files")
            for file in uploaded_files:
                file_size = f"{file.size / 1024:.1f} KB" if file.size < 1024*1024 else f"{file.size / (1024*1024):.1f} MB"
                st.markdown(f"• **{file.name}** ({file_size})")

        if st.button("Upload Documents", type="primary", disabled=not uploaded_files):
            progress_bar = st.progress(0)
            status_text = st.empty()

            success_count = 0
            total_files = len(uploaded_files)

            for i, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Processing: {uploaded_file.name}")
                progress_bar.progress((i + 1) / total_files)

                text_content = extract_text_from_uploaded_file(uploaded_file)

                if text_content and text_content.strip():
                    title = uploaded_file.name.rsplit('.', 1)[0]
                    st.session_state.agent.add_document(
                        title=title,
                        content=text_content,
                        source=f"Upload: {uploaded_file.name}",
                        metadata={
                            "file_type": uploaded_file.type,
                            "file_size": uploaded_file.size,
                            "upload_date": str(datetime.now().date())
                        }
                    )
                    success_count += 1
                    st.success(f"✅ Processed: {uploaded_file.name}")
                else:
                    st.error(f"❌ Failed to process: {uploaded_file.name}")

            status_text.text("Upload complete")
            if success_count > 0:
                st.success(f"Successfully uploaded {success_count} of {total_files} documents")

    else:  # Knowledge Base page
        st.markdown("## Knowledge Base")
        st.markdown("View and manage your document collection.")

        try:
            import sqlite3
            conn = sqlite3.connect(st.session_state.agent.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT title, source, COUNT(*) as chunk_count,
                       MIN(created_at) as created_at, metadata
                FROM documents
                GROUP BY title, source
                ORDER BY created_at DESC
            ''')

            documents = cursor.fetchall()
            conn.close()

            if documents:
                st.markdown(f"**Total Documents: {len(documents)}**")

                for doc in documents:
                    title, source, chunk_count, created_at, metadata_json = doc

                    with st.expander(f"📄 {title}"):
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.markdown(f"**Source:** {source}")
                        with col2:
                            st.markdown(f"**Chunks:** {chunk_count}")
                        with col3:
                            st.markdown(f"**Added:** {created_at}")

                        # Show metadata if available
                        if metadata_json:
                            try:
                                metadata = json.loads(metadata_json)
                                if metadata:
                                    st.markdown("**Metadata:**")
                                    for key, value in metadata.items():
                                        st.markdown(f"- {key}: {value}")
                            except:
                                pass

                        # Preview
                        conn = sqlite3.connect(st.session_state.agent.db_path)
                        cursor = conn.cursor()
                        cursor.execute(
                            "SELECT content FROM documents WHERE title = ? LIMIT 1",
                            (title,)
                        )
                        preview = cursor.fetchone()
                        conn.close()

                        if preview:
                            st.markdown("**Preview:**")
                            preview_text = preview[0][:300] + "..." if len(preview[0]) > 300 else preview[0]
                            st.text(preview_text)
            else:
                st.info("No documents in the knowledge base. Upload documents to get started.")

        except Exception as e:
            st.error(f"Error loading knowledge base: {str(e)}")

if __name__ == "__main__":
    main()