#!/usr/bin/env python3
import logging
import re

import auditor
import config
import core

log = logging.getLogger(__name__)

_FTS_UNSAFE = re.compile(r"['\"\\\(\)\[\]\{\}\+\-\!\:\^\~\*\?]")
_history: dict[str, list[dict]] = {}


def _get_history(eid):
    return _history.setdefault(eid, [])


def _append_history(eid, role, text):
    history = _get_history(eid)
    history.append({"role": role, "text": text})
    # Keep last 20 messages
    if len(history) > 20:
        _history[eid] = history[-20:]


def _format_history(history):
    lines = []
    for msg in history:
        speaker = "User" if msg["role"] == "user" else "VEL"
        lines.append(f"{speaker}: {msg['text']}")
    return "\n".join(lines)


def _search_archive(query, query_vec, eid, archive):
    safe_query = _FTS_UNSAFE.sub(" ", query).strip()
    # Try hybrid search first
    try:
        return (
            archive.search(query_type="hybrid")
            .vector(query_vec)
            .text(safe_query)
            .where(f"eid = '{eid}'")
            .limit(config.TOP_K)
            .to_list()
        )
    except (RuntimeError, ValueError) as err:
        log.warning("Hybrid search failed, fallback to vector only: %s", err)

    # Fallback vector search
    try:
        return (
            archive.search(query_vec, query_type="vector")
            .where(f"eid = '{eid}'")
            .limit(config.TOP_K)
            .to_list()
        )
    except (RuntimeError, ValueError) as err:
        log.error("Vector search failed for %s: %s", eid, err)
        return []


def chat(query, eid, embed_model, main_model, registry, archive):
    # Load entity facts
    try:
        facts = registry.search().where(f"eid = '{eid}'").to_list()
        attr_str = facts[0]["attrs"] if facts else "{}"
    except (RuntimeError, KeyError) as err:
        log.warning("Registry lookup failed for %s: %s", eid, err)
        attr_str = "{}"

    # Retrieve relevant chunks
    try:
        q_vec = core.embed(query, embed_model)
        results = _search_archive(query, q_vec, eid, archive)
        context = (
            "\n---\n".join(r["text"] for r in results)
            if results
            else "No relevant documents found."
        )
    except (RuntimeError, ValueError, KeyError) as err:
        log.error("Archive search failed for %s: %s", eid, err)
        context = "No relevant documents found."

    # Build conversation history
    history = _get_history(eid)
    history_str = (
        _format_history(history) if history else "No previous messages this session."
    )

    # Prompt construction
    prompt = (
        "<|im_start|>system\n"
        "You are VEL aka Velmira, a helpful local AI assistant. Answer only the user's current question. "
        "Do not invent follow-up questions or continue the conversation yourself.\n\n"
        f"Persistent facts about {eid}: {attr_str}\n"
        f"Relevant document context: {context}\n"
        "Conversation so far:\n"
        f"{history_str}<|im_end|>\n"
        "<|im_start|>user\n"
        f"{query}<|im_end|>\n"
        "<|im_start|>assistant\n"
    )

    # Stream response
    response_parts = []
    try:
        print("VEL:", end=" ", flush=True)
        for chunk in main_model(
            prompt,
            stream=True,
            temperature=config.TEMPERATURE,
            max_tokens=config.MAX_TOKENS,
            stop=["<|im_end|>", "<|im_start|>", "\nQuestion:", "\nUser:"],
        ):
            token = chunk["choices"][0]["text"]
            print(token, end="", flush=True)
            response_parts.append(token)
        print()
    except (RuntimeError, KeyError, IndexError) as err:
        log.error("Generation failed: %s", err)
        print(f"\nGeneration failed: {err}")
        return

    full_response = "".join(response_parts).strip()

    # Update history
    _append_history(eid, "user", query)
    _append_history(eid, "assistant", full_response)

    # Extract new facts from exchange
    try:
        exchange = f"User: {query}\nVEL: {full_response}"
        new_facts = auditor.extract_facts(exchange, eid, main_model)
        if new_facts:
            core.update_registry(registry, eid, new_facts)
    except (RuntimeError, KeyError, ValueError) as err:
        log.warning("Fact extraction failed: %s", err)
