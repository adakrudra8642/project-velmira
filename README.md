# VELMIRA (VEL)

> A local-first personal AI that turns any compatible model into a private document-aware tool for your data.

---

## What It Does

Vel reads your documents, indexes them locally, and answers questions from their content — no cloud, no API keys, no data leaving your machine. Privacy and GDPR compliance are built in.

Give VEL a document and ask anything. It finds relevant chunks, uses them as context, and generates answers with a local LLM on CPU only.

Multi-entity support lets you keep separate memory spaces for different people or projects. Switch context with a single command.

Better model, better responses.

---

## Quick Start

Download two GGUF models and place them in the `models/` folder (create it if it doesn't exist):

| Role | Type | Size | Quantization |
|------|------------|------|--------------|
| Main model | `gguf` | `4B` | `Q4_K_M` |
| Embedding model | `gguf` | `0.6B` | `q8_0` |

Both available on [Hugging Face](https://huggingface.co). Model path settings are now managed in `.env`; future versions will add a GUI for configuration.

```bash
chmod +x run.sh
./run.sh
```
or
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
[user] > set:rudra
[rudra] > read:research_paper.pdf
    Reading research_paper.pdf for rudra...
    Done. Facts found: {"name": "Rudra Adak", "role": "student", "institution": "XYZ"}
[rudra] > What methodology did they use?
    VEL: The paper uses a mixed-methods approach combining...
[rudra] > exit
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
- **Hybrid search** — vector similarity + full-text search combined. FTS failure degrades to vector-only.
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
├── src/
│   ├── __init__.py
│   ├── main.py          # Entry point, command loop
│   ├── core.py          # Model init, LanceDB, embed()
│   ├── chat.py          # RAG query + streaming + history
│   ├── docs.py          # Ingestion, chunking, Docling
│   ├── auditor.py       # Fact extraction
│   └── config.py        # Paths, model settings
├── models/              # GGUF files (not tracked)
│   ├── Main model
│   └── Embed model
├── data/                # Runtime data (not tracked)
│   ├── memory/
│   │   ├── archive.lance/
│   │   └── registry.lance/
│   └── vel.log
├── .dockerignore
├── .env
├── .gitignore
├── .vel-built           # Generates after run (not tracked)
├── compose.yml
├── DEVLOG.md
├── Dockerfile
├── LICENCE
├── pyproject.toml
├── README.md
├── requirements.txt
└── run.sh               # Can run manually
```

---

## Roadmap

- [ ] Async ingestion and query pipeline
- [ ] File generation (MD, PDF, XLSX output)
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
