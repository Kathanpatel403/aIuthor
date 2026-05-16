# AIuthor — Full Build Plan & Assessment Reference

This document is the **single source of truth** for building the Gateway Digital **AIuthor** technical assessment. Open this repo (or this file) in a new Cursor chat and say **PHASE N** or **build [TASK NAME]** to continue incrementally.

---

## 1. Assessment summary (what you are building)

**Goal:** Given a user brief (topic, reader profile, length, tonality, genre), build an **agentic** system that produces a **publication-ready book** — full front and back matter, multi-tonality voice, **memory across chapters**, and prose a human would want to read.

**Evaluation focus:** Orchestration, grounding, memory, and voice — not a shallow demo.

### MUST-have requirements

1. **Agentic pipeline** (not one prompt). Minimum agents: **Planner, Researcher, Writer, Humanizer, Editor, Fact-Checker, Memory Keeper, Assembler**. Document orchestration pattern (DAG, orchestrator-worker, or event-driven) and **coordination contracts**.

2. **Publication-ready book**
   - **Front matter:** half-title, title, copyright (ISBN placeholder, edition, rights, CIP block), dedication, epigraph, TOC, foreword, preface, acknowledgments, introduction.
   - **Body:** chapters with consistent structure and **real callbacks**.
   - **Back matter:** afterword, appendix, glossary (from in-book terms), references, about-the-author, back-cover copy.
   - **Deliverables:** **PDF + DOCX** with working TOC, **roman-numeral front matter**, **page numbers from the introduction**.

3. **Tonality as a first-class parameter.** Minimum **5 presets** — Conversational, Academic, Storyteller, Motivational, Witty — cascading through **every surface** (prose, preface, afterword, glossary defs, about-the-author, back-cover copy), **not only chapter bodies**.

4. **Humanize** — the book talks to the reader. Second-person where tonality supports it, hooks, domain metaphors, varied rhythm, memory-backed callbacks. Eliminate AI tells. **Humanizer rules MUST appear in the prompts dossier.**

5. **Memory across chapters:** fact registry, concept/character bible, callback index, tonality fingerprint, decision log. A single stuffed context window does **not** count. **Inserting a new chapter** MUST trigger correct **downstream repair** (TOC, callbacks, glossary).

6. **Observability.** Per run: agent trace, complete prompt log, memory I/O log, token and cost ledger.

### AI capabilities to apply (justify in design log)

- **RAG:** chunking, embedding model, vector store, top-k, hybrid/dense/BM25, reranking. No ungrounded freestyling on factual claims.
- **Tool use:** retrieval, memory R/W, web search, fact-check, structured extractors — clean contracts.
- **Structured outputs:** outlines, fact registry, callback index via JSON schema / typed outputs.
- **Preference-based refinement:** e.g. preference pairs, reward-model-lite tonality scorer, or LLM-as-judge with rubric; be ready to explain scale-up to DPO/RLHF.
- **Evals:** structural completeness, tonality fidelity, AI-tell detection, fact coverage, callback recall — ship rubric, runs, scores.
- **Guardrails:** fact-checker with abstention, citation-or-soften, **no fabricated references** implying real works.
- **Model strategy:** mixed models, document routing and cost rationale.
- **Context-window management:** compression, summarization, memory-backed retrieval.

### Rejection gates (do not violate)

- Missing or hidden prompts dossier  
- Single-prompt pipeline pretending to be agents  
- Missing MUST-have book structure  
- Tonality only on chapter bodies  
- No traces or logs  
- Fabricated references implying real works  
- **Test D** continuity / repair fails  

### Submission (typical)

- Repo link, demo link, sample-books ZIP, prompts dossier as standalone PDF  
- Timeline: **3 calendar days** (per assessment)

---

## 2. Master rules for how we work in Cursor

### Plan rules

1. Break work into **PHASES 1–8** (below).
2. Each phase has **TASKS**; each task should fit **1–2 hours** max.
3. For every task (when executing): what to build, which files, inputs/outputs, libraries, how to test before moving on.
4. **Never combine backend + frontend in the same task.**
5. **Always backend first, then frontend** for each feature.
6. **Every agent:** own Python file, own prompt module, **typed Pydantic contracts.**

### How to continue in a new chat

1. Attach or `@` this **README.md** (or the whole repo).
2. Say **`PHASE N`** to get **only** that phase in full detail (tasks, files, installs, test commands).
3. Say **`build [TASK NAME]`** to get **code for that task only** — no skipping ahead.
4. Do not ask the assistant to dump all phases at once unless you explicitly want a wall of text.

### Tech stack (fixed unless you change it)

| Layer | Choice |
|--------|--------|
| Backend | Python, **FastAPI**, **LangGraph**, **Pydantic** |
| Generation LLM | **GPT**  |
| Extraction / judging LLM | **GPT** |
| Vector DB | **Pinecone** |
| Memory store | **In memory cache** (persistent book state) (not having redis setup)|
| Embeddings | OpenAI **text-embedding-3-small** |
| Reranker | **Pinecone Inference** (`cohere-rerank-3.5`, same `PINECONE_API_KEY`) |
| RAG sources | user PDF uploads |
| PDF | **WeasyPrint** |
| DOCX | **python-docx** |
| Frontend | **React + Vite + Tailwind** |
| Observability | **LangSmith** |

---

## 3. Target repository layout

Repo root holds **two apps**: Python API under `backend/`, Vite UI under `frontend/` (no frontend inside Python).

```
demo_gateway/
├── backend/
│   ├── requirements.txt
│   ├── .env.example              # copy → backend/.env
│   ├── aiuthor/
│   │   ├── agents/               # Phase 5
│   │   ├── orchestrator/
│   │   ├── memory/               # Phase 2 (in-process store default)
│   │   ├── rag/
│   │   ├── tonality/
│   │   ├── humanizer/
│   │   ├── assembler/
│   │   ├── evals/
│   │   ├── observability/
│   │   ├── prompts/
│   │   ├── api/
│   │   │   ├── main.py
│   │   │   └── routes/
│   │   │       ├── generate.py
│   │   │       ├── memory.py
│   │   │       └── evals.py
│   │   └── schemas/
│   └── tests/
├── frontend/
│   ├── package.json
│   ├── .env.example              # copy → frontend/.env (VITE_*)
│   └── src/
│       ├── pages/                # Phase 8
│       └── components/
├── docs/
├── sample_books/
├── traces/
├── docker-compose.yml
├── Makefile
└── README.md
```

---

## 4. Phases — overview (detail on demand: type PHASE N)

### PHASE 1 — Project scaffolding & environment

**Goal:** Repo set up, dependencies, env vars, FastAPI runs, base schemas, LangSmith config.

**Tasks to cover:**

- Init repo, `.gitignore`, `backend/.env.example`, `frontend/.env.example`
- Python: `backend/requirements.txt` + install
- Frontend: `frontend/package.json` + install
- `backend/aiuthor/api/main.py` — FastAPI + health check
- Base Pydantic schemas: `UserBrief`, `BookOutline`
- LangSmith tracing config
- **Verify:** `make run-backend` and `make run-frontend` (or `make install` first)

---

### PHASE 2 — Memory layer

**Goal:** All five memory surfaces work with a **process-local in-memory store** by default (no Redis). Agents read/write through typed modules; chapter insert triggers **repair** across facts, concepts, and callbacks. Redis remains a future swap behind `AIUTHOR_MEMORY_BACKEND`.

**Tasks to cover:**

- `InMemoryMemoryStore` + thread-safe `BookMemoryState`
- `FactRegistry`, `ConceptBible`, `CallbackIndex` (+ `trigger_repair_after_chapter_insert`), `TonalityFingerprint`, `DecisionLog`
- `repair_after_chapter_insert` coordinator (Test D)
- API: `GET /api/memory/{book_id}` (empty snapshot if book never written); `POST /api/memory/{book_id}/chapter-insert-repair` (creates shell book if needed, then shifts indices)
- Unit tests per store (`make test-backend`)
- **Verify:** write fact → read via GET; run repair after insert → chapter indices shift

---

### PHASE 3 — RAG pipeline

**Goal:** Researcher ingests sources and retrieves grounded facts per chapter.

**Tasks to cover:**

- Wikipedia adapter (fetch + clean)
- Tavily web search adapter
- PDF adapter (e.g. PyPDF2 → text)
- Chunking (~500 tokens, ~50 overlap — tune to tokenizer)
- Embed with `text-embedding-3-small` → Pinecone
- Dense retrieval (top-k)
- BM25 keyword retrieval
- Hybrid merge (dense + BM25)
- Cohere rerank **via Pinecone Inference** only (`PINECONE_API_KEY` + `PINECONE_RERANK_MODEL`, e.g. `cohere-rerank-3.5`) — no separate Cohere API
- `ChapterFactPack` schema
- **Verify:** `make test` (RAG unit tests) or `POST /api/rag/chapter-fact-pack` with keys set → ≥1 grounded chunk; with full keys + corpus size, aim for ≥5 reranked chunks

---

### PHASE 4 — Tonality system

**Goal:** 5 presets; any surface can be toned consistently.

**Tasks to cover:**

- `tonality/presets.py` — Conversational, Academic, Storyteller, Motivational, Witty: vocab/rhythm/hooks/second-person flags/example openings
- `tonality/cascader.py` — `(surface_label, tone) →` system prompt modifier
- Fingerprint: embed sample → store reference vector per tone
- LLM-as-judge: fidelity score 0–1
- **Verify:** cascader on “glossary definition” for all 5 tones → distinct modifiers (and/or sample outputs in tests)

---

### PHASE 5 — Agent pipeline (core)

**Goal:** Eight agents implemented, tested, then **LangGraph** DAG.

**Order:**

| ID | Agent | Prompts module | Agent module | Core I/O |
|----|--------|----------------|--------------|----------|
| 5A | Planner | `planner_prompts.py` | `planner.py` | `UserBrief` → `BookOutline` (JSON schema) |
| 5B | Researcher | `researcher_prompts.py` | `researcher.py` | Chapter topic → `ChapterFactPack` (RAG) |
| 5C | Writer | `writer_prompts.py` | `writer.py` | outline + facts + memory + tone → `RawChapterDraft` |
| 5D | Humanizer | `humanizer_prompts.py` + `humanizer/rules.py` | `humanizer.py` | raw → `HumanizedDraft`; `humanizer/scorer.py` judge |
| 5E | Editor | `editor_prompts.py` | `editor.py` | humanized + `CallbackIndex` → `EditedDraft` + callbacks |
| 5F | Fact-checker | `fact_checker_prompts.py` | `fact_checker.py` | edited + `FactRegistry` → flags / soften / abstain |
| 5G | Memory keeper | `memory_keeper_prompts.py` | `memory_keeper.py` | post-chapter → update Redis stores |
| 5H | Assembler | `assembler_prompts.py` | `assembler/*.py` | full book → PDF + DOCX (TOC, roman front, arabic from intro) |
| 5I | LangGraph | `orchestrator/dag.py`, `contracts.py`, `router.py` | retries/fallbacks | E2E smoke: 3-chapter brief → PDF |

**Tests (examples):**

- Planner: PF brief, 10 chapters → valid outline  
- Researcher: “budgeting basics” → ≥5 sourced facts  
- Writer: ch.1 readable, minimal AI tells  
- Humanizer: inject “delve into” / “it's important to note” → removed + scorer violations  
- Editor: ch.3 callbacks to ch.1 concept  
- Fact-checker: fabricated claim → flagged/softened  
- Memory keeper: after ch.2 → registry + callbacks updated  
- Assembler: 3-chapter mini-book → valid PDF + DOCX  

---

### PHASE 6 — Observability layer

**Goal:** Every run emits a **trace bundle**.

**Implemented:** timing spans per LangGraph step, OpenAI prompt + usage logs, memory-store audit hooks, USD ledger estimates — persisted under `demo_gateway/traces/{book_id}/`.

**Tasks / artifacts:**

- `observability/agent_tracer.py` — `trace_span()` timing entries appended to collector  
- `observability/prompt_logger.py` — logs each LLM system/user + response preview  
- `observability/memory_audit.py` — memory read/write lines (wired into stores + repair + memory API)  
- `observability/token_cost_ledger.py` — per-call tokens + estimated USD (`PRICE_*` in `.env`)  
- `observability/bundle.py` — writes `manifest.json`, `agent_trace.json`, `prompts.jsonl`, `memory_io.jsonl`, `token_cost_ledger.json` after each pipeline run (also on pipeline failure)  
- API: **`GET /api/traces/{book_id}`** — manifest + file size stats  
- **Verify:** run pipeline → inspect `traces/{book_id}/` + hit traces API  

---

### PHASE 7 — Evals suite

**Goal:** Automated evals post-generation; JSON report + failure notes.

**Implemented:** weighted rubric (structural 0.25, tonality 0.20, AI-tells 0.20, callbacks 0.15, fact coverage 0.20).

**Tasks / artifacts:**

- `evals/structural_check.py` — required `# ...` headings for front/body/back  
- `evals/tonality_eval.py` — OpenAI embedding cosine vs preset exemplar text  
- `evals/ai_tell_detector.py` — Humanizer rule-list penalties  
- `evals/callback_recall.py` — keyword overlap callbacks ↔ chapter bodies  
- `evals/fact_coverage.py` — fact registry claims ↔ body keyword overlap  
- `evals/runner.py` → writes **`traces/{book_id}/evals_report.json`**  
- API: **`POST /api/evals/{book_id}?target_tonality=conversational`** — optional JSON body `{ "markdown_override": "..." }`  
- **Verify:** generate a book → POST evals → check scores + `evals_report.json`  

---

### PHASE 8 — Frontend (only after APIs exist)

**Goal:** UI for brief → run → preview → download → Test D insert.

**8A — Home:** form (topic, audience, tone, length, genre) → `POST /api/generate` → `book_id` → navigate to Pipeline.

**8B — Pipeline:** poll `GET /traces/{book_id}` ~2s; cards per agent (status, tokens); current chapter; progress bar.

**8C — Preview:** `GET /books/{book_id}/preview`; sidebar chapters + content; tone badge.

**8D — Downloads:** PDF/DOCX buttons; eval score card; link to trace bundle.

**8E — Test D UI:** Preview → “Insert Chapter” modal (after chapter N, topic) → `POST /api/insert-chapter` → repair status (TOC, callbacks, glossary).

---

## 5. Assessment test cases (run last; artifacts in `sample_books/`)

### Test A

- Brief: Beginner's guide to personal finance  
- Tone: **Conversational**  
- Chapters: **10**, ~**2,500** words each  
- Output: `sample_books/test_a/` — PDF + DOCX + trace bundle  

### Test B

- Brief: 5-chapter novella; characters **Maya** and **Rohan**  
- Tone: **Storyteller**  
- Chapters: **5**  
- Output: `sample_books/test_b/`  

### Test C

- Use **Test A outline**; regenerate **Chapter 3 only** in **Academic**, **Motivational**, and **Witty** (three variants).  
- Output: `sample_books/test_c/` — 3× PDF + DOCX  

### Test D

- Start from **Test A full book**  
- **Insert** new chapter **between Chapter 4 and 5**  
- Topic: **“The Psychology of Spending”**  
- Must self-heal: **TOC renumber**, **callbacks in ch.5–10**, **glossary** new terms  
- Output: `sample_books/test_d/` — updated PDF + DOCX + traces  

---

## 6. Deliverables checklist (submission)

- [ ] **Prompts dossier PDF** — every agent, every prompt, purpose, inputs, outputs, failure modes, why this prompt  
- [ ] **Working MVP** — one-command runnable (e.g. `make run-backend` / `make run-frontend` + optional docker-compose)  
- [ ] **Source repo** — honest commit history  
- [ ] **Architecture doc** — one diagram + ~one page (topology, stores, data flow, failure paths)  
- [ ] **Memory schema** — concrete models + example records  
- [ ] **Evals report** — rubric, runs, scores, failure analysis  
- [ ] **Trace bundle** — trace + prompt log + memory I/O + token/cost for **all four** tests  
- [ ] **Sample books** — PDF + DOCX for A, B, C, D  
- [ ] **Demo video** — 5–8 min, no deceptive edits  
- [ ] **Design decisions log** — **10** consequential decisions + rationale  

---

## 7. Phase completion verification (quick reference)

| Phase | Quick verify |
|-------|----------------|
| 1 | `make run-backend` + `make run-frontend` + `/health` |
| 2 | `make test-backend` + memory GET + insert-repair POST |
| 3 | `make test` + `POST /api/rag/chapter-fact-pack` (`OPENAI_API_KEY`; optional Tavily + Pinecone for dense/rerank) |
| 4 | `cascade_system_modifier` + `score_tonality_fidelity` (OpenAI mini judge) |
| 5 | `POST /api/generate/pipeline/run` + LangGraph; outputs under `sample_books/{book_id}/` |
| 6 | Pipeline run → `traces/{book_id}/manifest.json` + `GET /api/traces/{book_id}` |
| 7 | `POST /api/evals/{book_id}` → `evals_report.json` |
| 8 | Full UI flow + insert-chapter flow |

---

## 8. Cursor handoff line

**Ready.** In a new chat, attach this file and type **`PHASE 1`** (or `PHASE 2`, …) for step-by-step detail, or **`build [TASK NAME]`** for code only.

---

*Document generated for Gateway Digital AIuthor assessment — internal planning use.*
