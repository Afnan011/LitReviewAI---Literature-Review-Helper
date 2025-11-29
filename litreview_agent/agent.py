import os
import json
import arxiv
from duckduckgo_search import DDGS
from dotenv import load_dotenv
from google.adk.agents import LlmAgent, SequentialAgent, LoopAgent
from google.adk.models.google_llm import Gemini
from google.genai import types

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("WARNING: GOOGLE_API_KEY not found in .env file. Agent may fail to initialize.")

# ============================================================================
# TOOL DEFINITIONS
# ============================================================================

def search_papers_tool(query: str) -> str:
    """
    Searches for research papers on ArXiv and Web.
    Args:
        query: The research topic to search for.
    Returns:
        A JSON string containing a list of papers.
    """
    print(f"DEBUG: Search tool called with query: {query}")
    papers = []
    
    # 1. ArXiv Search
    try:
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
    except Exception as e:
        print(f"ArXiv error: {e}")

    # 2. Web Search (DDGS)
    try:
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
    except Exception as e:
        print(f"Web search error: {e}")
    
    print(f"DEBUG: Found {len(papers)} papers")
    return json.dumps(papers)

# ============================================================================
# AGENT DEFINITIONS
# ============================================================================

# Configure Retry Options
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

# Initialize global model for root agent
model = Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config)

# Factory function to create the workflow (must be called inside the correct event loop)
def create_internal_workflow():
    # Initialize model (re-initialized per call to avoid loop binding issues)
    # We use a new instance for the thread
    thread_model = Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config)

    # 1. Search Agent
    search_agent = LlmAgent(
        name="SearchAgent",
        model=thread_model,
        instruction="""
        You are a Research Librarian.
        Your goal is to find a broad list of research papers for a given query.
        Use the `search_papers_tool` to get the raw data.
        
        Output: Return the raw JSON list of papers found.
        """,
        tools=[search_papers_tool],
        description="Searches for research papers on ArXiv and Web"
    )

    # 2. Selection Agent
    selection_agent = LlmAgent(
        name="SelectionAgent",
        model=thread_model,
        instruction="""
        You are a Senior Editor.
        Input: The list of research papers provided by the previous agent.
        Task: Select the **top 5** most relevant and high-quality papers.
        
        Sorting Logic:
        - Prioritize papers with a known Year.
        - Sort the final 5 papers by Year (Descending/Newest First).
        - The JSON array MUST be ordered such that index 0 is the newest paper.
        
        Output: Return the SORTED JSON list of 5 papers.
        """,
        description="Selects top 5 papers from search results"
    )

    # 3. Extraction Agent
    extraction_agent = LlmAgent(
        name="ExtractionAgent",
        model=thread_model,
        instruction="""
        You are a Research Analyst.
        Input: The list of 5 selected papers provided by the previous agent.
        Task: For each paper, extract:
        - key_findings
        - methodology
        - relevance
        
        Output: Return the enriched JSON list with these details added.
        """,
        description="Extracts key findings from papers"
    )

    # 4. Synthesis Agent (Iterative)
    synthesis_agent = LlmAgent(
        name="SynthesisAgent",
        model=thread_model,
        instruction="""
        You are an Academic Writer.
        Input: 
        - First run: A list of 5 analyzed papers.
        - Subsequent runs: Your previous draft AND the Reviewer's feedback.
        
        Task: Write (or rewrite) a comprehensive literature review report.
        
        If you receive feedback, use it to IMPROVE your draft. Fix any issues mentioned.
        
        CRITICAL OUTPUT FORMAT:
        - Write EXACTLY 5 paragraphs, one for each paper.
        - **ORDER**: Discuss papers in the exact order provided (which is sorted by date).
        - **PARAGRAPH START**: Start EACH paragraph with the first author's name and "et al." (e.g., "Pan et al. ...").
        - **CITATION**: End each paragraph with a sequential citation marker: [1], [2], [3], [4], [5].
        
        - **REFERENCES SECTION**:
          Add a "### References" section at the end.
          You MUST format this as a list.
          CRITICAL: Put a BLANK LINE (double newline) between each reference.
          
          Example format:
          [1] Title, Authors, Year, URL
          
          [2] Title, Authors, Year, URL
          
          [3] Title, Authors, Year, URL
          ...
        
        Output: Return the full literature review text.
        """,
        description="Writes literature review report"
    )

    # 5. Evaluation Agent (Iterative)
    evaluation_agent = LlmAgent(
        name="EvaluationAgent",
        model=thread_model,
        instruction="""
        You are a Reviewer.
        Input: The literature review report provided by the previous agent.
        Task: Evaluate if it follows the 5-paragraph format and has correct citations.
        
        OUTPUT:
        - First, provide your Score (1-10) and brief feedback.
        - Then, output the ORIGINAL literature review text exactly as received.
        
        If the score is low (< 8), be very specific about what needs to be fixed in your feedback.
        
        IMPORTANT: You are the final step of the loop. Return the full review text.
        """,
        description="Evaluates literature review quality"
    )

    # Refinement Loop
    # Cycles between Synthesis and Evaluation to improve quality
    refinement_loop = LoopAgent(
        name="RefinementLoop",
        description="Iteratively improves the literature review",
        sub_agents=[synthesis_agent, evaluation_agent],
        max_iterations=2 # Run twice: Draft -> Eval -> Refine -> Final Eval
    )

    # Internal Workflow (Sequential)
    return SequentialAgent(
        name="InternalLitReviewWorkflow",
        description="Internal workflow for literature review",
        sub_agents=[
            search_agent,
            selection_agent,
            extraction_agent,
            refinement_loop 
        ]
    )

from google.adk.runners import InMemoryRunner
import asyncio

# ... (previous agent definitions remain the same) ...

# Tool to run the workflow and return ONLY the final text
def execute_literature_review(topic: str) -> str:
    """
    Executes the full literature review workflow for a given topic.
    Returns the final formatted literature review text.
    """
    print(f"DEBUG: Starting internal workflow for topic: {topic}")
    
    async def run_internal():
        # Create the workflow agents INSIDE the correct loop/thread context
        internal_workflow = create_internal_workflow()
        runner = InMemoryRunner(agent=internal_workflow)
        
        # Run the workflow
        result = await runner.run_debug(topic)
        
        # Extract the final text from the last event
        final_text = "Error: No output generated."
        
        # Iterate backwards to find the last meaningful text output
        for event in reversed(result):
            if hasattr(event, 'content') and event.content:
                if hasattr(event.content, 'parts'):
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            return part.text.strip()
                            
        return final_text

    # Run the async workflow in a separate thread to avoid event loop conflicts
    import threading
    
    result_container = {}
    
    def thread_target():
        try:
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result_container['output'] = loop.run_until_complete(run_internal())
            loop.close()
        except Exception as e:
            result_container['error'] = str(e)
            import traceback
            traceback.print_exc()
            
    thread = threading.Thread(target=thread_target)
    thread.start()
    thread.join()
    
    if 'error' in result_container:
        return f"Error executing workflow: {result_container['error']}"
        
    output = result_container.get('output', "Error: No output produced")
    print(f"DEBUG: Tool returning output of length {len(output)}")
    return output

# Public Facing Agent
# This is what the user interacts with. It just calls the tool.
root_agent = LlmAgent(
    name="LitReviewAI",
    model=model,
    description="LitReview AI - Your AI-powered literature review assistant",
    instruction="""
    You are LitReview AI.
    When a user asks for a literature review, use the `execute_literature_review` tool.
    
    IMPORTANT: The tool will return the full literature review text.
    You MUST copy that text and send it as your final response to the user.
    Do not summarize it. Just output the full text you received from the tool.
    """,
    tools=[execute_literature_review]
)

# Alias for ADK Web discovery
agent = root_agent
