# 🤖 LitReview AI

> Advanced AI-Powered Literature Review Assistant
> 
> Built with Google Agent Development Kit (ADK) | Capstone Project for Google's 5-Day AI Agent Intensive Course

## ✨ Features

- **🔍 Intelligent Paper Search**: Automatically searches ArXiv and web sources for relevant research papers
- **🎯 Smart Selection**: AI-powered selection of the top 5 most relevant papers
- **📊 Key Findings Extraction**: Automated extraction of methodology, findings, and relevance
- **✍️ Professional Synthesis**: Generates well-structured literature reviews with proper citations
- **⭐ Quality Evaluation**: Built-in evaluation system that scores the generated review

## 🏗️ Architecture

LitReview AI uses a **multi-agent architecture** with 5 specialized AI agents:

```
┌─────────────────────────────────────────┐
│        LitReview AI Coordinator         │
│     (Orchestrates the workflow)         │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┼──────────┬──────────┬──────────┐
    │          │          │          │          │
┌───▼───┐  ┌──▼──┐  ┌────▼───┐  ┌──▼──┐  ┌────▼────┐
│Search │  │Select│  │Extract │  │Synth│  │Evaluate │
│Agent  │  │Agent │  │ Agent  │  │Agent│  │ Agent   │
└───────┘  └─────┘  └────────┘  └─────┘  └─────────┘
   📚         🎯         📊         ✍️         ⭐
```

### Agent Details

1. **SearchAgent** 📚
   - Searches ArXiv database for academic papers
   - Performs web searches for additional sources
   - Returns up to 40 papers (20 from each source)

2. **SelectionAgent** 🎯
   - Analyzes all found papers
   - Ranks by relevance and quality
   - Selects top 5 papers
   - Sorts by publication year (newest first)

3. **ExtractionAgent** 📊
   - Extracts key findings from each paper
   - Identifies methodology used
   - Assesses relevance to the query

4. **SynthesisAgent** ✍️
   - Writes a professional literature review
   - Creates 5 paragraphs (one per paper)
   - Adds proper citations [1], [2], etc.
   - Includes a references section

5. **EvaluationAgent** ⭐
   - Reviews the generated literature review
   - Checks format compliance
   - Verifies citation accuracy
   - Provides quality score (1-10) and feedback

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

### Interactive CLI Mode

Run the interactive command-line interface:

```bash
python litreview_ai.py
```

The CLI provides a beautiful menu-driven interface:

- **Option 1**: Start a new literature review
- **Option 2**: View information about LitReview AI
- **Option 3**: Exit the application

### Features of Interactive Mode

- 🎨 **Colored output** for better readability
- 📝 **Auto-save** - Reviews are automatically saved with timestamps
- ⏳ **Progress indicators** for each step
- 🖥️ **User-friendly** menu system

### Example Session

```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║               🤖 LitReview AI - v1.0                          ║
║                                                               ║
║        Advanced AI-Powered Literature Review Assistant        ║
║        Powered by Google ADK Multi-Agent System               ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

✅ API key loaded
⏳ Initializing LitReview AI agents...
✅ All agents initialized successfully!

┌─────────────────────────────────────────────────────────┐
│                     MAIN MENU                           │
├─────────────────────────────────────────────────────────┤
│  1. 📚 Start New Literature Review                     │
│  2. ℹ️  About LitReview AI                             │
│  3. 🚪 Exit                                             │
└─────────────────────────────────────────────────────────┘

Enter your choice (1-3): 1

Enter your research topic: Multi-Agent Systems in AI

🔍 Processing Query
==================
Query: Multi-Agent Systems in AI

⏳ Starting literature review process...
...
```

### Jupyter Notebook Mode

For Kaggle or local Jupyter environments, use:

```bash
jupyter notebook literature-review-updated.ipynb
```

## 📁 Project Structure

```
Literature Review Helper/
├── litreview_ai.py              # Interactive CLI application
├── literature-review-updated.ipynb  # Jupyter notebook version
├── .env                         # API keys (create this)
├── requirements.txt             # Python dependencies
├── README.md                    # This file
└── review_*.txt                 # Generated reviews (auto-created)
```

## 📦 Dependencies

- `google-adk` - Google Agent Development Kit
- `google-generativeai` - Google Gemini API
- `arxiv` - ArXiv API wrapper
- `duckduckgo-search` - Web search capability
- `python-dotenv` - Environment variable management

Install all dependencies:
```bash
pip install google-generativeai arxiv duckduckgo-search ddgs python-dotenv google-adk
```

## 🎯 Use Cases

- **Academic Research**: Quickly get an overview of research in a specific field
- **Literature Surveys**: Generate comprehensive literature reviews
- **Research Planning**: Identify key papers and research directions
- **Proposal Writing**: Gather background information for research proposals

## 🔧 Configuration

### Model Selection

By default, LitReview AI uses `gemini-2.5-flash-lite`. You can change this in `litreview_ai.py`:

```python
model = Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config)
```

Available models:
- `gemini-2.5-flash-lite` (fastest, default)
- `gemini-2.5-flash` (balanced)
- `gemini-2.0-pro` (most powerful)

### Search Parameters

Adjust search volume in the `search_papers_tool` function:

```python
search = arxiv.Search(query=query, max_results=20, ...)  # Change max_results
results = list(ddgs.text(keywords, max_results=20))      # Change max_results
```

## 🤝 Contributing

This is a capstone project for Google's AI Agent Intensive Course. Feel free to fork and adapt for your own use!

## 📝 License

MIT License - Feel free to use and modify

## 🙏 Acknowledgments

- Built with Google's Agent Development Kit (ADK)
- Created for Google's 5-Day AI Agent Intensive Course
- Powered by Gemini 2.5 Flash

## 📧 Contact

For questions or feedback about this project, please open an issue on GitHub.

---

**Made with ❤️ using Google ADK** | **Capstone Project** | **2025**
