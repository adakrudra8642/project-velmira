import json
import logging

import lancedb
from llama_cpp import Llama

import config

log = logging.getLogger(__name__)

def init():
    print("Initializing VEL Kernel...")
    # Load models
    embed_model = Llama(model_path=config.EMBED_MODEL, **config.EMBED_CONFIG, embedding=True)
    main_model = Llama(model_path=config.MAIN_MODEL, **config.MAIN_CONFIG)

    # Get embedding dimension
    try:
        dimension = len(embed_model.create_embedding("test")["data"][0]["embedding"])
    except Exception as e:
        log.critical("Embedding model failed: %s", e)
        raise RuntimeError("Could not get embedding dimension.") from e

    # Connect to LanceDB
    db = lancedb.connect(config.DB_PATH)
    registry = db.create_table("registry", data=[{"eid": "init", "attrs": "{}"}], exist_ok=True)
    archive = db.create_table("archive",
        data=[{"id": "init", "eid": "sys", "text": "Init", "vector": [0.0]*dimension}],
        exist_ok=True)

    # Try FTS index (optional)
    try:
        archive.create_fts_index("text", replace=True)
    except Exception as e:  # noqa: BLE001
        log.warning("FTS index failed, vector-only search: %s", e)
        print("Warning: FTS unavailable. Vector search only.")

    return embed_model, main_model, registry, archive

def embed(text, model):
    try:
        return model.create_embedding(text)["data"][0]["embedding"]
    except Exception as e:
        log.error("Embedding failed for '%s...': %s", text[:50], e)
        raise

def update_registry(table, eid, new_attrs):
    if not isinstance(new_attrs, dict) or not new_attrs:
        return
    try:
        existing = table.search().where(f"eid = '{eid}'").to_list()
        if existing:
            current = json.loads(existing[0]["attrs"])
            current.update(new_attrs)
            table.update(where=f"eid = '{eid}'", values={"attrs": json.dumps(current)})
        else:
            table.add([{"eid": eid, "attrs": json.dumps(new_attrs)}])
    except Exception as e:  # noqa: BLE001
        log.error("Registry update failed for %s: %s", eid, e)
