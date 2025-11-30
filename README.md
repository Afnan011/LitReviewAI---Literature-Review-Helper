# 🤖 LitReview AI

> Advanced AI-Powered Literature Review Assistant
> 
> Built with Google Agent Development Kit (ADK) | Capstone Project for Google's 5-Day AI Agent Intensive Course

## ✨ Features

- **🔍 Intelligent Paper Search**: Automatically searches ArXiv and web sources for relevant research papers
- **🎯 Smart Selection**: AI-powered selection of the top 5 most relevant papers
- **📊 Key Findings Extraction**: Automated extraction of methodology, findings, and relevance
- **✍️ Professional Synthesis**: Generates well-structured literature reviews with proper citations
- **🔄 Iterative Refinement**: **[NEW]** Self-correcting loop that improves the review based on AI critique
- **⭐ Quality Evaluation**: Built-in evaluation system that scores the generated review
- **💬 Interactive Web Chat**: Clean, chat-based interface using `adk web`

## 🏗️ Architecture

LitReview AI uses a **multi-agent architecture** with a deterministic sequential workflow and an iterative refinement loop.

```mermaid
graph TD
    User[User] -->|Query| Root[Root Agent (LitReviewAI)]
    Root -->|Calls Tool| Tool[execute_literature_review Tool]
    
    subgraph "Internal Encapsulated Workflow (Threaded)"
        Tool --> Search[Search Agent]
        Search -->|Raw Papers| Select[Selection Agent]
        Select -->|Top 5 Papers| Extract[Extraction Agent]
        Extract -->|Enriched Data| LoopStart((Start Loop))
        
        subgraph "Iterative Refinement Loop (Max 2)"
            LoopStart --> Synth[Synthesis Agent]
            Synth -->|Draft Review| Eval[Evaluation Agent]
            Eval -->|Critique & Score| Synth
        end
        
        Eval -->|Final Review| Result[Final Output]
    end
    
    Result -->|Text| Tool
    Tool -->|Response| Root
    Root -->|Chat Message| User

    style Root fill:#f9f,stroke:#333,stroke-width:2px
    style Tool fill:#bbf,stroke:#333,stroke-width:2px
    style Search fill:#dfd,stroke:#333,stroke-width:1px
    style Select fill:#dfd,stroke:#333,stroke-width:1px
    style Extract fill:#dfd,stroke:#333,stroke-width:1px
    style Synth fill:#ffd,stroke:#333,stroke-width:1px
    style Eval fill:#ffd,stroke:#333,stroke-width:1px
```

### Agent Details

1. **SearchAgent** 📚
   - Searches ArXiv database and Web (DuckDuckGo)
   - Returns up to 40 papers (20 from each source)

2. **SelectionAgent** 🎯
   - Analyzes all found papers
   - Selects top 5 papers based on relevance and year
   - Sorts by publication year (newest first)

3. **ExtractionAgent** 📊
   - Extracts key findings, methodology, and relevance for each paper

4. **SynthesisAgent** ✍️
   - Writes a professional literature review
   - Creates 5 paragraphs (one per paper)
   - Adds proper citations [1], [2], etc.
   - **Self-Correction**: Improves draft based on feedback from EvaluationAgent

5. **EvaluationAgent** ⭐
   - Reviews the generated literature review
   - Checks format compliance and citation accuracy
   - Provides quality score (1-10) and specific feedback for improvement

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- Google API Key ([Get it here](https://aistudio.google.com/))

### Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd "Literature Review Helper"
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Key**
   
   Create a `.env` file in the project directory:
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   ```

## 💻 Usage

### Web Chat Interface (Recommended)

Run the ADK Web server to interact with the agent in a clean chat interface:

```bash
./venv/Scripts/adk web --port 8080
```

Then open your browser at `http://localhost:8080` and type your request:
> "Write a literature review on deep learning"

### CLI Mode

You can also run the agent directly via CLI (for debugging):

```bash
./venv/Scripts/adk run litreview_agent "Write a literature review on deep learning"
```

## 📁 Project Structure

```
Literature Review Helper/
├── litreview_agent/             # ADK Agent Package
│   ├── __init__.py              # Package marker
│   └── agent.py                 # Main agent definition & logic
├── litreview_ai.py              # Legacy CLI application
├── literature-review-updated.ipynb  # Jupyter notebook version
├── .env                         # API keys
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 📦 Dependencies

- `google-adk` - Google Agent Development Kit
- `google-generativeai` - Google Gemini API
- `arxiv` - ArXiv API wrapper
- `duckduckgo-search` - Web search capability
- `python-dotenv` - Environment variable management

## 🔧 Configuration

### Model Selection

By default, LitReview AI uses `gemini-2.5-flash-lite`. You can change this in `litreview_agent/agent.py`.

### Search Parameters

Adjust search volume in the `search_papers_tool` function in `litreview_agent/agent.py`.

## 🤝 Contributing

This is a capstone project for Google's AI Agent Intensive Course. Feel free to fork and adapt for your own use!

## 📝 License

MIT License - Feel free to use and modify

## 🙏 Acknowledgments

- Built with Google's Agent Development Kit (ADK)
- Created for Google's 5-Day AI Agent Intensive Course
- Powered by Gemini 2.5 Flash

---

**Made with ❤️ using Google ADK** | **Capstone Project** | **2025**
