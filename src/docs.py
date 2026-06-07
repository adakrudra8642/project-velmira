import logging
import time
from pathlib import Path

from docling.document_converter import DocumentConverter

import auditor
import core

log = logging.getLogger(__name__)
converter = DocumentConverter()

def chunk_text(text, size=500, overlap=50):
    words = text.split()
    chunks = []
    idx = 0
    while idx < len(words):
        chunk = " ".join(words[idx:idx+size])
        chunks.append(chunk)
        idx += size - overlap
    return [c for c in chunks if len(c) > 30]

def read_file(path, eid, embed_model, main_model, registry, archive):
    print(f"Reading '{path}' for '{eid}'...")
    try:
        # Convert document to markdown
        content = converter.convert(path).document.export_to_markdown()
        # Extract facts and update registry
        facts = auditor.audit_file(content, eid, main_model)
        core.update_registry(registry, eid, facts)

        # Chunk and embed
        chunks = chunk_text(content)
        filename = Path(path).name
        rows = []
        for i, chunk in enumerate(chunks):
            rows.append({
                "id": f"{filename}_{i}_{int(time.time())}",
                "eid": eid,
                "text": chunk,
                "vector": core.embed(chunk, embed_model),
            })
        archive.add(rows)
        print(f"Done. {len(chunks)} chunks stored. Facts: {facts}")
    except Exception as e:  # noqa: BLE001
        log.error("Failed to process '%s' for '%s': %s", path, eid, e)
        print(f"Error processing file: {e}")
