## Development Log

**Genesis note:** This project was restarted from scratch on 07‑Jun‑2026 after a local Git history corruption. All current code is stable and represents the **V1.0.0** release. No functionality was lost – the reset only cleaned up internal version control.

**V1.0.0** — Official Public Release ^_^
**Release Date:** Tue 17/Feb/2026 · 19:28:10 IST Mumbai(Naigaon E)

**V0.5.2** — Documentation & Build Configuration
- Expanded README with comprehensive setup instructions, architecture diagrams, and tech stack details.
- Added `pyproject.toml` for modern Python packaging and dependency management.
- Refined `requirements.txt` with pinned versions for reproducibility.
- Standardized formatting, improved clarity, and corrected documentation inconsistencies.

**V0.5.1** — Hardening & Architecture Cleanup
- Fixed silent bug: embedding and generation models shared config, causing pooling_type to corrupt generation outputs.
- Replaced print debugging with structured logging to data/vel.log for traceability.
- Auditor now uses regex JSON fallback and logs errors instead of silently returning {}.
- Entity IDs validated by regex before DB queries to prevent injection-like issues.
- File paths checked against extension whitelist for early failure, avoiding cryptic Docling errors.
- FTS index creation failure is non-fatal; falls back to vector-only search with warning.
- Auditor prompt capped at 3000 chars to prevent context overflow and garbage JSON.

**V0.4.3** — Stable RAG
- End-to-end testing on real documents produced correct answers.
- Fixed streaming output artifacts that made responses appear broken.
- Core RAG loop is now feature-stable: embed → search → inject → generate.

**V0.4.2** — Document Q&A Finally Working
- Resolved embedding dimension mismatch between query and stored chunks.
- .txt ingestion works end-to-end, validating full RAG pipeline.
- First working Q&A: user question → embedding → retrieval → context injection → answer generation.

**V0.4.1** — Architecture Reset
- Removed overcomplicated dual-model memory system; too many failure points.
- Refactored to single responsibility per module; simplified design.
- Adopted strict rule: only add features that solve immediate problems.

**V0.3.2** — Vector Database
- Integrated LanceDB for persistent vector storage across sessions.
- Dedicated embedding model (Qwen 0.6B) separate from generation model.
- Implemented basic similarity search with configurable top-K.

**V0.3.1** — Learning from Failure
- Attempted dual-model (summarizer + responder) failed due to complexity and debugging nightmare.
- Gained deeper understanding of RAG patterns: store chunks, retrieve, inject as context.
- Simplified approach: vector DB + retrieval + context injection.

**V0.2.0** — Modular Refactor
- Split monolithic prototype into focused modules with clear responsibilities.
- Rebuilt streaming to fix race condition causing incomplete responses.
- Established maintainable structure for future development.

**V0.1.2** — Hardware Calibration
- Tested 3B–8B quantized models on 16GB RAM CPU.
- 8B too slow (20+ sec/response); 3B fast but weak reasoning.
- Settled on 4B Q4_K_M: 5–10 tok/sec, good quality for interactive use.

**V0.1.1** — Foundation
- Set up Python venv, confirmed llama-cpp-python loads a model.
- Created project directory structure and Git repo.

**V0.0.1** — Concept
- Scoped down ambitious vision to minimal viable: ask question about document, get correct answer.
- Defined core constraints: local-only, CPU-only, 16GB RAM max.
