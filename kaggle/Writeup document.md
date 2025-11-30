# LitReview AI: Your Intelligent Research Assistant 📚🤖

> **Capstone Project for Google's 5-Day AI Agent Intensive Course**

### Problem Statement
Conducting a comprehensive literature review is one of the most time-consuming and daunting tasks for researchers and students. It involves:
1.  **Endless Searching**: Sifting through hundreds of search results across multiple databases (ArXiv, Google Scholar, etc.).
2.  **Information Overload**: Reading dozens of abstracts to find the few that are actually relevant.
3.  **Manual Synthesis**: Extracting key findings and methodology from each paper and weaving them into a coherent narrative.
4.  **Citation Management**: Ensuring every claim is backed by a correct citation.

This manual process is slow, prone to bias, and often results in important papers being missed. **LitReview AI** aims to solve this by automating the entire pipeline—from discovery to the final written report—reducing days of work into minutes.

### Why agents?
A single Large Language Model (LLM) prompt (e.g., "Write a literature review on X") often fails because:
*   **Hallucination**: It may invent papers or citations.
*   **Context Window**: It can't browse the live web or access up-to-date ArXiv papers effectively in one go.
*   **Lack of Structure**: It struggles to maintain a strict format (e.g., "exactly 5 paragraphs") while simultaneously analyzing complex technical content.

**Agents are the right solution because they allow for specialization:**
*   A **Search Agent** can focus solely on querying APIs.
*   A **Selection Agent** acts as a strict filter, ensuring only high-quality papers pass through.
*   A **Synthesis Agent** can focus on writing, while a separate **Evaluation Agent** critiques the work.
This "Assembly Line" approach ensures high reliability, accuracy, and adherence to strict formatting rules that a single model call simply cannot match.

### What you created
I built **LitReview AI**, a multi-agent system orchestrated by Google's Agent Development Kit (ADK).

**The Architecture:**
The system follows a **Sequential Workflow** with an embedded **Iterative Refinement Loop**:

1.  **Search Agent 🔍**: Queries **ArXiv** and the **Web** (DuckDuckGo) to gather a broad pool of potential papers.
2.  **Selection Agent 🎯**: Acts as a "Senior Editor," analyzing the raw list to select the **top 5** most relevant papers, sorting them by publication year (newest first).
3.  **Extraction Agent 📊**: Deeply analyzes the selected papers to extract specific details: Key Findings, Methodology, and Relevance.
4.  **Refinement Loop 🔄**:
    *   **Synthesis Agent ✍️**: Drafts the review using a strict 5-paragraph format with citations.
    *   **Evaluation Agent ⭐**: Critiques the draft for formatting and citation accuracy.
    *   *Self-Correction*: If the score is low, the Synthesis Agent rewrites the draft based on the feedback.

### Demo
*(Note: In the Kaggle notebook, you can see the full execution logs showing this process in action.)*

**Input:**
> "Multi-Agent Systems in Healthcare"

**Process:**
1.  **Search**: Found 40 papers (20 ArXiv, 20 Web).
2.  **Selection**: Narrowed down to the 5 most recent and relevant papers (e.g., "Agent-Based Modeling for Epidemics (2024)", "Federated Learning in Medical AI (2023)").
3.  **Extraction**: Extracted that Paper A used "Reinforcement Learning" while Paper B focused on "Privacy-Preserving Architecture."
4.  **Synthesis**: Drafted a review.
5.  **Evaluation**: "Score: 9/10. Good citations, but ensure the reference list has blank lines." -> *Final Polish*.

**Output:**
A perfectly formatted, 5-paragraph literature review with a "References" section, ready to be copy-pasted into a research paper.

### The Build
This project was built using:
*   **Google Agent Development Kit (ADK)**: For defining the `SequentialAgent`, `LoopAgent`, and `LlmAgent` primitives.
*   **Gemini 2.5 Flash Lite**: The core intelligence powering all agents. It's fast, cost-effective, and has a large context window perfect for analyzing multiple papers.
*   **ArXiv API**: For fetching academic papers directly.
*   **DuckDuckGo Search (`ddgs`)**: For broad web searches to catch recent blog posts or industry whitepapers.
*   **Kaggle Secrets**: For secure API key management.

**Key Technical Challenge Solved:**
Managing the **Refinement Loop**. I used ADK's `LoopAgent` to create a feedback cycle where the writer and reviewer agents talk to each other. This significantly improved the quality of the final output compared to a single-pass generation.

### If I had more time, this is what I'd do
1.  **Full PDF Parsing (RAG)**: Currently, the agents analyze abstracts. With more time, I would implement RAG (Retrieval-Augmented Generation) to download and "read" the full PDF content of the papers for deeper analysis.
2.  **Dynamic Planning**: Instead of a fixed "Top 5" papers, I'd add a "Planner Agent" that decides *how many* papers are needed based on the complexity of the user's query.
3.  **Web Interface**: Deploy the `adk web` interface to a public URL (like Hugging Face Spaces) so non-coders can use it easily.
