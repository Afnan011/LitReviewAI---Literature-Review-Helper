"""
🤖 LitReview AI - Web Interface
Advanced Literature Review Assistant with Web UI
"""

import os
import json
import asyncio
import arxiv
from typing import List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv
from duckduckgo_search import DDGS
import streamlit as st

# Google ADK Imports
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.genai import types


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="LitReview AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .stAlert {
        border-radius: 10px;
    }
    .agent-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# TOOL DEFINITIONS
# ============================================================================

def search_papers_tool(query: str) -> str:
    """
    Searches for research papers on ArXiv and Web.
    """
    papers = []
    
    # 1. ArXiv Search
    try:
        with st.spinner("🔍 Searching ArXiv database..."):
            arxiv_client = arxiv.Client()
            search = arxiv.Search(query=query, max_results=20, sort_by=arxiv.SortCriterion.Relevance)
            for result in arxiv_client.results(search):
                papers.append({
                    "title": result.title,
                    "url": result.entry_id,
                    "abstract": result.summary.replace("\n", " "),
                    "authors": ", ".join([a.name for a in result.authors]),
                    "year": result.published.year,
                    "source": "ArXiv"
                })
            st.success(f"✅ Found {len(papers)} ArXiv papers")
    except Exception as e:
        st.error(f"❌ ArXiv error: {e}")

    # 2. Web Search
    try:
        with st.spinner("🌐 Searching web sources..."):
            with DDGS() as ddgs:
                keywords = f"{query} research paper"
                results = list(ddgs.text(keywords, max_results=20))
                for r in results:
                    papers.append({
                        "title": r.get('title', 'No Title'),
                        "url": r.get('href', ''),
                        "abstract": r.get('body', ''),
                        "authors": "Unknown",
                        "year": "Unknown",
                        "source": "Web"
                    })
            st.success(f"✅ Found {len(results)} web results")
    except Exception as e:
        st.error(f"⚠️ Web search error: {e}")
    
    st.info(f"📊 Total papers found: {len(papers)}")
    return json.dumps(papers)


# ============================================================================
# AGENT INITIALIZATION
# ============================================================================

@st.cache_resource
def initialize_agents(api_key: str):
    """Initialize all AI agents (cached)"""
    
    # Configure Retry Options
    retry_config = types.HttpRetryOptions(
        attempts=5,
        exp_base=7,
        initial_delay=1,
        http_status_codes=[429, 500, 503, 504],
    )
    
    # Initialize model
    model = Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config)
    
    # 1. Search Agent
    search_agent = LlmAgent(
        name="SearchAgent",
        model=model,
        instruction="""
        You are a Research Librarian.
        Your goal is to find a broad list of research papers for a given query.
        Use the `search_papers_tool` to get the raw data.
        Return the raw JSON list of papers found.
        """,
        tools=[search_papers_tool],
        description="Searches for research papers on ArXiv and Web"
    )
    
    # 2. Selection Agent
    selection_agent = LlmAgent(
        name="SelectionAgent",
        model=model,
        instruction="""
        You are a Senior Editor.
        Input: A JSON list of research papers.
        Task: Select the **top 5** most relevant and high-quality papers.
        
        Sorting Logic:
        - Prioritize papers with a known Year.
        - Sort the final 5 papers by Year (Descending/Newest First).
        
        Output: Return ONLY a JSON array of the 5 selected paper objects.
        """,
        description="Selects top 5 papers from search results"
    )
    
    # 3. Extraction Agent
    extraction_agent = LlmAgent(
        name="ExtractionAgent",
        model=model,
        instruction="""
        You are a Research Analyst.
        Input: A JSON list of 5 papers.
        Task: For each paper, extract:
        - key_findings
        - methodology
        - relevance
        
        Output: Return the same JSON list but with these new fields added to each paper object.
        """,
        description="Extracts key findings from papers"
    )
    
    # 4. Synthesis Agent
    synthesis_agent = LlmAgent(
        name="SynthesisAgent",
        model=model,
        instruction="""
        You are an Academic Writer.
        Input: A JSON list of 5 analyzed papers.
        Task: Write a literature review report.
        
        Strict Format:
        1. Exactly 5 paragraphs (one per paper).
        2. End each paragraph with a citation marker [1], [2], etc.
        3. Add a '### References' section at the end with full details.
        
        Do not add any other intro or conclusion text. Just the report.
        """,
        description="Writes literature review report"
    )
    
    # 5. Evaluation Agent
    evaluation_agent = LlmAgent(
        name="EvaluationAgent",
        model=model,
        instruction="""
        You are a Reviewer.
        Input: A literature review report.
        Task: Evaluate if it follows the 5-paragraph format and has correct citations.
        Output: A score (1-10) and brief feedback.
        """,
        description="Evaluates literature review quality"
    )
    
    # Coordinator Agent
    coordinator = LlmAgent(
        name="LitReviewAI",
        model=model,
        description="LitReview AI - Your AI-powered literature review assistant",
        instruction="""
        You are LitReview AI, an advanced AI assistant for conducting literature reviews.
        Your task is to coordinate a multi-agent literature review process.
        
        Workflow:
        1. Use SearchAgent to find papers
        2. Use SelectionAgent to select top 5 papers
        3. Use ExtractionAgent to extract key details
        4. Use SynthesisAgent to write the review
        5. Use EvaluationAgent to evaluate the review
        
        Return the final evaluated report with the synthesis and evaluation.
        Be professional, thorough, and helpful.
        """,
        sub_agents=[
            search_agent,
            selection_agent,
            extraction_agent,
            synthesis_agent,
            evaluation_agent
        ]
    )
    
    return coordinator


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    # Header
    st.markdown('<h1 class="main-header">🤖 LitReview AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Advanced AI-Powered Literature Review Assistant</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        # Load API key
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            st.error("❌ GOOGLE_API_KEY not found in .env file!")
            st.info("Please create a .env file with your Google API key")
            st.stop()
        
        st.success("✅ API Key loaded")
        
        st.markdown("---")
        st.markdown("### 🤖 Multi-Agent System")
        st.markdown("""
        **5 Specialized Agents:**
        - 📚 SearchAgent
        - 🎯 SelectionAgent
        - 📊 ExtractionAgent
        - ✍️ SynthesisAgent
        - ⭐ EvaluationAgent
        """)
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown("""
        LitReview AI uses Google's ADK framework with 
        Gemini 2.5 Flash to provide comprehensive 
        literature reviews automatically.
        
        **Built for:** Google's 5-Day AI Agent Intensive Course
        """)
    
    # Main content
    st.markdown("### 📝 Start a New Literature Review")
    
    query = st.text_input(
        "Enter your research topic:",
        placeholder="e.g., Multi-Agent Systems in Large Language Models",
        help="Enter a research topic to generate a comprehensive literature review"
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        generate_button = st.button("🚀 Generate Review", type="primary", use_container_width=True)
    
    with col2:
        clear_button = st.button("🗑️ Clear", use_container_width=True)
    
    if clear_button:
        st.rerun()
    
    if generate_button and query:
        st.markdown("---")
        
        # Initialize agents
        with st.spinner("🔧 Initializing AI agents..."):
            try:
                coordinator = initialize_agents(api_key)
                runner = InMemoryRunner(agent=coordinator)
                st.success("✅ All agents initialized successfully!")
            except Exception as e:
                st.error(f"❌ Failed to initialize agents: {e}")
                st.stop()
        
        # Progress tracking
        st.markdown("### 🔄 Processing Literature Review")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Run the review
        try:
            status_text.text("🔍 Step 1/5: Searching for papers...")
            progress_bar.progress(20)
            
            # Create containers for displaying outputs
            output_container = st.container()
            
            # Create async task using run_debug (matches working notebook)
            async def run_review():
                # Use run_debug which returns the final response
                response = await runner.run_debug(query)
                return response
            
            
            # Execute with simulated progress
            status_text.text("🎯 Step 2/5: Selecting top papers...")
            progress_bar.progress(40)
            
            status_text.text("📊 Step 3/5: Extracting key findings...")
            progress_bar.progress(60)
            
            status_text.text("✍️ Step 4/5: Writing literature review...")
            progress_bar.progress(80)
            
            # Run the review
            response = asyncio.run(run_review())
            
            status_text.text("⭐ Step 5/5: Evaluating quality...")
            progress_bar.progress(100)
            st.success("✅ Literature review completed!")
            
            # Debug: Show response type
            with st.expander("🔍 Debug Info (click to expand)"):
                st.write(f"Response type: {type(response)}")
                st.write(f"Response length: {len(str(response))} characters")
                if isinstance(response, list):
                    st.write(f"Number of events: {len(response)}")
                st.code(str(response)[:500] + "..." if len(str(response)) > 500 else str(response))
            
            # Parse the response
            synthesis_text = ""
            evaluation_text = ""
            
            # Handle different response types
            if isinstance(response, str):
                # Direct string response
                final_response = response
            elif isinstance(response, list):
                # List of events
                for event in response:
                    try:
                        # Check if event has author and content
                        if hasattr(event, 'author') and hasattr(event, 'content'):
                            author = event.author
                            content = event.content
                            
                            # Extract text from content parts
                            if hasattr(content, 'parts') and content.parts:
                                for part in content.parts:
                                    if hasattr(part, 'text') and part.text:
                                        text = part.text.strip()
                                        
                                        # Skip empty text or debugging output
                                        if not text or text.startswith('Model:'):
                                            continue
                                        
                                        # Capture synthesis and evaluation
                                        if author == 'SynthesisAgent':
                                            synthesis_text = text
                                        elif author == 'EvaluationAgent':
                                            evaluation_text = text
                    except Exception as e:
                        st.error(f"Error parsing event: {e}")
                        continue
                
                # Build final response from extracted texts
                final_response = ""
                if synthesis_text:
                    final_response = f"## 📚 Literature Review\n\n{synthesis_text}"
                
                if evaluation_text:
                    final_response += f"\n\n---\n\n## ⭐ Quality Evaluation\n\n{evaluation_text}"
            else:
                # Unknown type, convert to string
                final_response = str(response)
            
            # Fallback if nothing was extracted
            if not final_response or len(final_response) < 50:
                final_response = """
## ⚠️ Unable to Extract Review

The literature review process completed, but we couldn't extract the formatted text.
This might be due to:
- The agents are still processing
- The response format has changed
- Network issues

**Please try again with a different query or check the console for details.**
"""
            
            # Display results
            st.markdown("---")
            st.markdown("### 📄 Generated Literature Review")
            
            # Create tabs for different views
            tab1, tab2 = st.tabs(["📖 Review", "💾 Download"])
            
            with tab1:
                st.markdown(final_response)
            
            with tab2:
                # Save to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"review_{timestamp}.txt"
                
                review_content = f"""LitReview AI - Literature Review
Query: {query}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}

{final_response}
"""
                
                st.download_button(
                    label="📥 Download Report",
                    data=review_content,
                    file_name=filename,
                    mime="text/plain",
                    use_container_width=True
                )
                
                st.info(f"💡 Report ready for download as: `{filename}`")
        
        except Exception as e:
            st.error(f"❌ Error during literature review: {e}")
            st.exception(e)
    
    elif generate_button and not query:
        st.warning("⚠️ Please enter a research topic first!")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        Made with ❤️ using Google ADK | Powered by Gemini 2.5 Flash | 2025
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
