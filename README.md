# AIuthor: Professional Multi-Agent Book Engine

AIuthor is a state-of-the-art multi-agent system designed to generate publication-quality books (Non-fiction & Novellas) with human-like prose, deep factual grounding, and self-healing structural integrity.

## 🚀 The Core Engine
Unlike simple LLM wrappers, AIuthor uses a **LangGraph-driven DAG** to orchestrate specialized agents:

1.  **Planner**: Architecting the book structure and audience-specific arc.
2.  **Researcher**: Multi-source RAG (Wikipedia, Tavily) to ground every claim.
3.  **Writer**: Produces prose with a "Memory-Backed" approach for cross-chapter continuity.
4.  **Humanizer**: Tightens rhythm, eliminates "AI tells," and enforces specific tonality.
5.  **Editor**: Weaves in subtle callbacks and ensures consistent character/concept arcs.
6.  **Fact Checker**: Verifies claims against the research pack before commitment.
7.  **Memory Keeper**: Indexes the "Concept Bible," "Fact Registry," and "Callback Index" for the entire book.
8.  **Assembler**: Generates professional Front Matter, Table of Contents, Glossary, and References.

## 🧠 Advanced Features
-   **Self-Healing Insertion**: Insert a chapter mid-book; the system auto-repairs the TOC, shifts all chapter-indexed memory, and re-calculates callbacks.
-   **Tone Cascading**: Real-time tonality variants (Academic, Motivational, Witty, etc.) for any chapter.
-   **Print-Ready Exports**: Professional PDF (Roman numeral front matter, page numbers) and DOCX layouts.
-   **Audit Suite**: A built-in testing dashboard to validate quality, scale, and recovery logic (Tests A-D).

## 🛠 Tech Stack
-   **Frontend**: React, Vite, TailwindCSS, Heroicons.
-   **Backend**: Python, FastAPI, LangGraph, Pydantic v2.
-   **LLMs**: OpenAI GPT-4o (Prose), GPT-4o-mini (Orchestration).
-   **Observability**: Integrated trace bundles and manifest-driven job tracking.

## 🏃 Quick Start

### Backend
1. `cd backend`
2. `python -m venv venv`
3. `source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
4. `pip install -r requirements.txt`
5. Create `.env` with `OPENAI_API_KEY` and `TAVILY_API_KEY`.
6. `uvicorn aiuthor.api.main:app --reload`

### Frontend
1. `cd frontend`
2. `npm install`
3. `npm run dev`

Navigate to the **Audit Suite** in the UI to run the standard validation sequence and generate your first professional guide or novella.
