# LitReview AI: Advanced Multi-Agent Literature Review Assistant

> **Capstone Project for Google's 5-Day AI Agent Intensive Course**

## 1. Project Overview

**LitReview AI** is an intelligent, multi-agent system designed to automate the laborious process of conducting academic literature reviews. By leveraging **Google's Agent Development Kit (ADK)** and the **Gemini 2.5 Flash** model, it autonomously searches for research papers, selects the most relevant ones, extracts key findings, and synthesizes a professional, citation-backed literature review.

### The Problem
Conducting a literature review is time-consuming. Researchers must:
1.  Search multiple databases (ArXiv, Google Scholar, etc.).
2.  Filter through hundreds of abstracts to find relevant papers.
3.  Read and extract methodology and findings.
4.  Synthesize this information into a coherent narrative.
5.  Format citations correctly.

### The Solution
LitReview AI automates this entire pipeline using a team of specialized AI agents, reducing hours of work to minutes.

---

## 2. Architecture

The system is built on a **Sequential Workflow** with an **Iterative Refinement Loop**. It uses a deterministic chain of agents to ensure quality and consistency.

### Agent Workflow
1.  **Search Agent** 📚: Queries ArXiv and the Web (via DuckDuckGo) to gather a broad pool of potential papers.
2.  **Selection Agent** 🎯: Acts as a senior editor, analyzing the raw search results to select the top 5 most relevant and high-quality papers, sorting them by publication year.
3.  **Extraction Agent** 📊: detailed analysis of the selected papers, extracting key findings, methodology, and relevance.
4.  **Refinement Loop** 🔄:
    *   **Synthesis Agent** ✍️: Drafts the literature review, following a strict 5-paragraph format with citations.
    *   **Evaluation Agent** ⭐: Critiques the draft, providing a quality score and feedback.
    *   The loop runs (up to 2 iterations) to allow the Synthesis Agent to self-correct and improve the review based on feedback.

### Technical Stack
*   **Framework**: Google Agent Development Kit (ADK)
*   **Model**: Gemini 2.5 Flash Lite
*   **Tools**: `arxiv` (API wrapper), `duckduckgo-search` (Web search)
*   **Environment**: Python 3.10+

---

## 3. Key Features

*   **Intelligent Search**: Combines academic databases (ArXiv) with general web search for comprehensive coverage.
*   **Deterministic Selection**: Ensures the "best" papers are chosen based on relevance, not just random selection.
*   **Structured Output**: Produces a standardized format (Introduction -> 5 Body Paragraphs -> References) that is easy to read.
*   **Self-Correction**: The unique "Refinement Loop" allows the AI to critique its own work and fix citation or formatting errors before showing the final result.
*   **Clean UI**: Designed to run as a web chat interface using `adk web` or as a standalone notebook.

---

## 4. Implementation Details

### Google ADK Integration
This project extensively uses Google ADK's core primitives:
*   **`LlmAgent`**: The building block for all specialized agents.
*   **`SequentialAgent`**: Orchestrates the linear flow from Search -> Selection -> Extraction.
*   **`LoopAgent`**: Manages the iterative cycle between Synthesis and Evaluation.
*   **`InMemoryRunner`**: Executes the agent workflow.

### Challenges & Solutions
*   **Challenge**: Getting consistent output formats (e.g., ensuring exactly 5 paragraphs).
    *   **Solution**: Implemented a strict "Evaluation Agent" that checks for formatting rules and rejects drafts that don't comply.
*   **Challenge**: Handling `asyncio` loops in different environments (Web vs Notebook).
    *   **Solution**: Used threading for the Web UI to isolate the agent's event loop, while keeping a clean async flow for the Notebook version.

---

## 5. Future Improvements
*   **More Sources**: Integrate PubMed and IEEE Xplore APIs.
*   **PDF Parsing**: Allow the agent to read full PDF papers instead of just abstracts.
*   **Dynamic Planning**: Allow the agent to decide how many papers to select based on the query complexity.

---

**Created by [Your Name]**
*Google AI Agent Intensive Capstone 2025*
