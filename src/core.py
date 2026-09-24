#!/usr/bin/env python3
import json
import logging

import lancedb
from llama_cpp import Llama

import config

log = logging.getLogger(__name__)


def init():
    # Initialize VEL kernel with models and database
    print("Initializing VEL Kernel...")

    # Load models
    embed_model = Llama(
        model_path=config.EMBED_MODEL, **config.EMBED_CONFIG, embedding=True
    )
    main_model = Llama(model_path=config.MAIN_MODEL, **config.MAIN_CONFIG)

    # Get embedding dimension
    try:
        embedding_response = embed_model.create_embedding("test")
        dimension = len(embedding_response["data"][0]["embedding"])
    except (KeyError, IndexError, RuntimeError) as err:
        log.critical("Embedding model failed to determine dimension: %s", err)
        raise RuntimeError("Could not get embedding dimension.") from err

    # Connect to LanceDB
    db = lancedb.connect(str(config.DB_PATH))
    registry = db.create_table(
        "registry", data=[{"eid": "init", "attrs": "{}"}], exist_ok=True
    )
    archive = db.create_table(
        "archive",
        data=[
            {"id": "init", "eid": "sys", "text": "Init", "vector": [0.0] * dimension}
        ],
        exist_ok=True,
    )

    # Try FTS index
    try:
        archive.create_fts_index("text", replace=True)
    except (RuntimeError, ValueError) as err:
        log.warning("FTS index failed, vector-only search enabled: %s", err)
        print("Warning: FTS unavailable. Vector search only.")

    return embed_model, main_model, registry, archive


def embed(text, model):
    # Create embedding for text
    try:
        embedding_response = model.create_embedding(text)
        return embedding_response["data"][0]["embedding"]
    except (KeyError, IndexError, RuntimeError) as err:
        log.error("Embedding failed for '%s...': %s", text[:50], err)
        raise


def update_registry(table, eid, new_attrs):
    # Update registry table with new attributes
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
    except (json.JSONDecodeError, KeyError, RuntimeError) as err:
        log.error("Registry update failed for %s: %s", eid, err)
