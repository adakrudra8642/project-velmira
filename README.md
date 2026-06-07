# VELMIRA (VEL)

> A local-first RAG assistant. Your documents stay on your machine. Always.

Vel reads your documents, indexes them into a local vector database, and answers questions about their content — no cloud, no API keys, no data leaving your machine. Built with privacy and GDPR compliance as first-class constraints, not afterthoughts.

---

## What It Does

Feed VEL a document. Ask it anything about that document. It retrieves the relevant chunks, injects them as context, and generates an answer using a fully local LLM. All of it runs on CPU — no GPU required.

Multi-entity support means you can maintain separate memory spaces for different people or projects. A hospital could track patient records. A school could separate student profiles. Switch context with a single command.

---

## Quick Start

```bash
git clone https://github.com/adakrudra8642/project-velmira.git
cd project-velmira

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS

pip install -r requirements.txt
```

Download two GGUF models and place them in the `models/` folder (create it if it doesn't exist):

| Role | Recommended Model |
|------|-------------------|
| Main LLM | `Qwen3-4B-*-Q4_K_M.gguf` |
| Embeddings | `Qwen3-Embedding-0.6B-q8_0.gguf` |

Both available on [Hugging Face](https://huggingface.co). Update paths in `src/config.py` if you use different models.

```bash
python src/main.py
```

---

## Usage

```
Commands:
    set:<name>    — Switch active entity context  (e.g. set:alice)
    read:<file>   — Index a document              (e.g. read:report.pdf)
    <question>    — Ask anything                  (e.g. What is the conclusion?)
    exit          — Quit

Entity IDs: letters, numbers, _ and - only. Max 64 chars.
```

**Example session:**

```
[user] > set:alice
[alice] > read:research_paper.pdf
    Reading research_paper.pdf for alice...
    Done. Facts found: {"name": "Alice Chen", "role": "researcher", "institution": "MIT"}
[alice] > What methodology did they use?
    VEL: The paper uses a mixed-methods approach combining...
[alice] > exit
```

---

## Architecture

```
User Input
    │
    ▼
Input Validation (entity ID sanitization, file extension whitelist)
    │
    ├── read:<file> ──► Docling parser ──► Chunker ──► Embed chunks ──► LanceDB
    │                          └──► Auditor (fact extraction) ──► Registry
    │
    └── <question> ──► Embed query ──► Hybrid search (vector + FTS)
                            └──► Top-K chunks + entity facts ──► Context injection
                                      └──► LLM stream ──► Terminal output
                                              └──► vel.log
```

**Key design decisions:**

- **Two separate model configs** — embedding model uses `pooling_type=1`, generation model does not. Sharing config caused silent misbehavior in earlier versions.
- **Hybrid search** — vector similarity + full-text search combined. FTS failure degrades gracefully to vector-only.
- **Append-only registry** — entity facts are merged, never overwritten blind. Conflict detection is logged.
- **Input sanitization** — entity IDs validated by regex before hitting any DB query. File paths checked against extension whitelist.

---

## Tech Stack

| Component | Library |
|-----------|---------|
| LLM inference | llama-cpp-python (CPU-only) |
| Vector DB | LanceDB (embedded, no server) |
| Document parsing | Docling (PDF, DOCX, MD, XLSX, PPTX) |
| Fact extraction | Custom auditor with regex JSON fallback |
| Logging | Python stdlib logging → `data/vel.log` |

**Hardware target:** 16GB RAM, no dedicated GPU. Tested on Intel Core Ultra 5 225H.

---

## Project Structure

```
project-velmira/
├── .gitignore
├── LICENSE
├── README.md
├── DEVLOG.md
├── pyproject.toml
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── main.py                 — Entry point, main loop
│   ├── core.py                 — Model init, DB, embed()
│   ├── chat.py                 — RAG query + streaming
│   ├── docs.py                 — Ingestion + chunking
│   ├── auditor.py              — Fact extraction
│   └── config.py               — Paths, model settings
├── models/                     — GGUF files (not tracked)
└── data/                       — LanceDB + logs (not tracked)
```

---

## Roadmap

- [ ] Async ingestion and query pipeline
- [ ] File generation (MD, PDF, XLSX output)
- [ ] Velmira desktop overlay (Godot 4 + always-on-top character)
- [ ] RPG-style chat bubbles
- [ ] File search and OS-level interaction
- [ ] TTS voice output
- [ ] Role-based entity access model (multi-user)

---

## Contributing

Early stage project — issues and PRs welcome. If you're building something local-AI related and want to collaborate, open an issue or reach out directly.

Rudra Adak -- adakrudra8642@gmail.com

---

## License

Apache License 2.0 — see [LICENSE](LICENSE) for details.

Built by Rudra Adak · 2025–2026
