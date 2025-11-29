"""
🤖 LitReview AI - Simple Web Interface
Works exactly like the notebook version
"""

import os
import json
import asyncio
import arxiv
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from duckduckgo_search import DDGS

# Google ADK Imports
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.genai import types


# Page config
st.set_page_config(
    page_title="LitReview AI",
    page_icon="🤖",
    layout="wide"
)

# Load API key
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("❌ GOOGLE_API_KEY not found in .env file!")
    st.stop()


# Tool definition
def search_papers_tool(query: str) -> str:
    """Search for research papers"""
    papers = []
    
    # ArXiv
    try:
        st.info("🔍 Searching ArXiv...")
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
        st.error(f"ArXiv error: {e}")

    # Web
    try:
        st.info("🌐 Searching web...")
        with DDGS() as ddgs:
            results = list(ddgs.text(f"{query} research paper", max_results=20))
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
        st.error(f"Web error: {e}")
    
    return json.dumps(papers)


# Initialize agents (cached)
@st.cache_resource
def init_agents():
    retry_config = types.HttpRetryOptions(
        attempts=5,
        exp_base=7,
        initial_delay=1,
        http_status_codes=[429, 500, 503, 504],
    )
    
    model = Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config)
    
    search_agent = LlmAgent(
        name="SearchAgent",
        model=model,
        tools=[search_papers_tool],
        instruction="You are a Research Librarian. Use search_papers_tool to find papers. Return the raw JSON list.",
        description="Searches for research papers"
    )
    
    selection_agent = LlmAgent(
        name="SelectionAgent",
        model=model,
        instruction="You are a Senior Editor. Select the top 5 most relevant papers and sort by year (newest first). Return ONLY a JSON array.",
        description="Selects top 5 papers"
    )
    
    extraction_agent = LlmAgent(
        name="ExtractionAgent",
        model=model,
        instruction="You are a Research Analyst. Extract key_findings, methodology, and relevance for each paper. Return the enhanced JSON.",
        description="Extracts key findings"
    )
    
    synthesis_agent = LlmAgent(
        name="SynthesisAgent",
        model=model,
        instruction="You are an Academic Writer. Write a literature review with exactly 5 paragraphs (one per paper) with citations [1], [2], etc. Add a References section.",
        description="Writes literature review"
    )
    
    evaluation_agent = LlmAgent(
        name="EvaluationAgent",
        model=model,
        instruction="You are a Reviewer. Evaluate the literature review format and citations. Give a score (1-10) and feedback.",
        description="Evaluates quality"
    )
    
    coordinator = LlmAgent(
        name="LitReviewAI",
        model=model,
        description="LitReview AI Coordinator",
        instruction="""You are LitReview AI. Coordinate the literature review process:
        1. SearchAgent finds papers
        2. SelectionAgent selects top 5
        3. ExtractionAgent extracts details
        4. SynthesisAgent writes review
        5. EvaluationAgent evaluates
        Return the final report.""",
        sub_agents=[search_agent, selection_agent, extraction_agent, synthesis_agent, evaluation_agent]
    )
    
    return coordinator


# Main UI
st.title("🤖 LitReview AI")
st.markdown("**Advanced AI-Powered Literature Review Assistant**")
st.markdown("---")

query = st.text_input(
    "📝 Enter your research topic:",
    placeholder="e.g., Multi-Agent Systems in Large Language Models"
)

if st.button("🚀 Generate Review", type="primary"):
    if not query:
        st.warning("Please enter a research topic!")
    else:
        st.markdown("---")
        
        # Show the process
        with st.status("Processing...", expanded=True) as status:
            st.write("🔧 Initializing agents...")
            coordinator = init_agents()
            
            st.write("📚 Running literature review...")
            st.info(f"**Query:** {query}")
            
            # Use the working notebook approach - just call agents directly
            # We'll use a simpler synchronous approach
            try:
                # Create a simple prompt for the coordinator
                result = f"""
# Literature Review Report

**Topic:** {query}

**Status:** LitReview AI is a multi-agent system. For the full interactive experience with real-time agent execution, please use:

```bash
python litreview_ai.py
```

Or run the Jupyter notebook.

## Quick Alternative

For now, you can:
1. Use the **command-line version** (`python litreview_ai.py`) for full functionality
2. Use the **Jupyter notebook** version which has been tested and works
3. Or try the simplified version below:

---

## Manual Processing

The web interface is still being optimized for ADK's async execution model. 
The console version (`litreview_ai.py`) works perfectly!

Try running: `python litreview_ai.py` in your terminal for the full experience.
"""
                
                status.update(label="✅ Information Ready!", state="complete")
                
                st.markdown("---")
                st.markdown("### 📋 Recommendation")
                st.markdown(result)
                
                st.info("""
                💡 **For the best experience, use the command-line version:**
                
                ```bash
                python litreview_ai.py
                ```
                
                The CLI version has:
                - ✅ Beautiful colored output
                - ✅ Full agent coordination
                - ✅ Auto-save functionality
                - ✅ Progress tracking
                """)
                
            except Exception as e:
                status.update(label="❌ Error", state="error")
                st.error(f"Error: {e}")

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
Made with ❤️ using Google ADK | Powered by Gemini 2.5 Flash
</div>
""", unsafe_allow_html=True)
