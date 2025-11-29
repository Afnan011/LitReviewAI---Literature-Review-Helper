#!/usr/bin/env python3
"""
🤖 LitReview AI - Advanced Literature Review Assistant
Powered by Google ADK Multi-Agent System
"""

import os
import json
import asyncio
import arxiv
from typing import List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv
from duckduckgo_search import DDGS

# Google ADK Imports
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.genai import types

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_banner():
    """Display the LitReview AI banner"""
    banner = f"""
{Colors.OKCYAN}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║               🤖 LitReview AI - v1.0                          ║
║                                                               ║
║        Advanced AI-Powered Literature Review Assistant        ║
║        Powered by Google ADK Multi-Agent System               ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
{Colors.ENDC}
"""
    print(banner)


def print_loading(message: str):
    """Print a loading message"""
    print(f"{Colors.OKCYAN}⏳ {message}...{Colors.ENDC}")


def print_success(message: str):
    """Print a success message"""
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")


def print_error(message: str):
    """Print an error message"""
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")


def print_info(message: str):
    """Print an info message"""
    print(f"{Colors.OKBLUE}ℹ️  {message}{Colors.ENDC}")


def print_section(title: str):
    """Print a section header"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{title.center(60)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}\n")


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
    print(f"\n{Colors.BOLD}🛠️ [Search Tool] Searching for: {query}{Colors.ENDC}")
    papers = []
    
    # 1. ArXiv Search
    try:
        print(f"{Colors.OKCYAN}   📚 Searching ArXiv database...{Colors.ENDC}")
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
        print_success(f"Found {len(papers)} ArXiv papers")
    except Exception as e:
        print_error(f"ArXiv error: {e}")

    # 2. Web Search (DDGS)
    try:
        print(f"{Colors.OKCYAN}   🌐 Searching web sources...{Colors.ENDC}")
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
        print_success(f"Found {len(results)} web results")
    except Exception as e:
        print_error(f"Web search error: {e}")
    
    print_info(f"Total papers found: {len(papers)}")
    return json.dumps(papers)


# ============================================================================
# AGENT INITIALIZATION
# ============================================================================

def initialize_agents(api_key: str):
    """Initialize all AI agents"""
    print_loading("Initializing LitReview AI agents")
    
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
    
    # Coordinator Agent (LitReview AI)
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
    
    print_success("All agents initialized successfully!")
    print_info("5 specialized agents ready:")
    print(f"   • {Colors.BOLD}SearchAgent{Colors.ENDC} - Finds research papers")
    print(f"   • {Colors.BOLD}SelectionAgent{Colors.ENDC} - Selects top 5 papers")
    print(f"   • {Colors.BOLD}ExtractionAgent{Colors.ENDC} - Extracts key findings")
    print(f"   • {Colors.BOLD}SynthesisAgent{Colors.ENDC} - Writes literature review")
    print(f"   • {Colors.BOLD}EvaluationAgent{Colors.ENDC} - Evaluates quality")
    
    return coordinator


# ============================================================================
# MAIN INTERACTIVE LOOP
# ============================================================================

└─────────────────────────────────────────────────────────┘{Colors.ENDC}
"""
    print(menu)


def show_about():
    """Display information about LitReview AI"""
    about = f"""
{Colors.OKCYAN}{Colors.BOLD}About LitReview AI{Colors.ENDC}

LitReview AI is an advanced AI-powered literature review assistant that uses
Google's Agent Development Kit (ADK) to provide comprehensive academic research
summaries.

{Colors.BOLD}Features:{Colors.ENDC}
  • Multi-agent collaboration for thorough analysis
  • Searches ArXiv and web sources for research papers
  • Intelligent paper selection and ranking
  • Automated key findings extraction
  • Professional literature review synthesis
  • Quality evaluation and scoring

{Colors.BOLD}Multi-Agent System:{Colors.ENDC}
  LitReview AI uses 5 specialized AI agents that work together:
  1. SearchAgent - Finds relevant research papers
  2. SelectionAgent - Selects the most relevant papers
  3. ExtractionAgent - Extracts key information
  4. SynthesisAgent - Writes the literature review
  5. EvaluationAgent - Evaluates the final report

{Colors.BOLD}Technology:{Colors.ENDC}
  Built with Google ADK and Gemini 2.5 Flash Lite

{Colors.BOLD}Created for:{Colors.ENDC}
  Google's 5-Day AI Agent Intensive Course Capstone Project
"""
    print(about)


async def main():
    """Main application entry point"""
    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print_banner()
    
    # Load environment variables
    load_dotenv()
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    if not GOOGLE_API_KEY:
        print_error("GOOGLE_API_KEY not found in .env file!")
        print_info("Please create a .env file with your Google API key")
        return
    
    print_success("API key loaded")
    
    # Initialize agents
    try:
        coordinator = initialize_agents(GOOGLE_API_KEY)
        runner = InMemoryRunner(agent=coordinator)
        print_success("LitReview AI is ready!")
    except Exception as e:
        print_error(f"Failed to initialize agents: {e}")
        return
    
    # Main loop
    while True:
        show_menu()
        choice = input(f"{Colors.BOLD}Enter your choice (1-3): {Colors.ENDC}").strip()
        
        if choice == '1':
            print_section("📝 New Literature Review")
            query = input(f"{Colors.BOLD}Enter your research topic: {Colors.ENDC}").strip()
            
            if query:
                await run_literature_review(runner, query)
                input(f"\n{Colors.OKCYAN}Press Enter to continue...{Colors.ENDC}")
            else:
                print_error("Query cannot be empty!")
                
        elif choice == '2':
            show_about()
            input(f"\n{Colors.OKCYAN}Press Enter to continue...{Colors.ENDC}")
            
        elif choice == '3':
            print_section("👋 Goodbye")
            print_info("Thank you for using LitReview AI!")
            print(f"{Colors.OKCYAN}Visit us again for your literature review needs!{Colors.ENDC}\n")
            break
            
        else:
            print_error("Invalid choice! Please enter 1, 2, or 3.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}⚠️  Interrupted by user{Colors.ENDC}")
        print_info("Goodbye!")
    except Exception as e:
        print_error(f"Fatal error: {e}")
