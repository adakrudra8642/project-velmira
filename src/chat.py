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
        return (archive.search(query_type="hybrid")
                .vector(query_vec)
                .text(safe_query)
                .where(f"eid = '{eid}'")
                .limit(config.TOP_K)
                .to_list())
    except Exception:  # noqa: BLE001
        log.warning("Hybrid search failed, fallback to vector only")
    # Fallback vector search
    try:
        return (archive.search(query_vec, query_type="vector")
                .where(f"eid = '{eid}'")
                .limit(config.TOP_K)
                .to_list())
    except Exception as e:  # noqa: BLE001
        log.error("Vector search failed for %s: %s", eid, e)
        return []

def chat(query, eid, embed_model, main_model, registry, archive):
    # Load entity facts
    try:
        facts = registry.search().where(f"eid = '{eid}'").to_list()
        attr_str = facts[0]["attrs"] if facts else "{}"
    except Exception:  # noqa: BLE001
        log.warning("Registry lookup failed for %s", eid)
        attr_str = "{}"

    # Retrieve relevant chunks
    try:
        q_vec = core.embed(query, embed_model)
        results = _search_archive(query, q_vec, eid, archive)
        context = "\n---\n".join(r["text"] for r in results) if results else "No relevant documents found."
    except Exception as e:  # noqa: BLE001
        log.error("Archive search failed for %s: %s", eid, e)
        context = "No relevant documents found."

    # Build conversation history
    history = _get_history(eid)
    history_str = _format_history(history) if history else "No previous messages this session."

    # Prompt
    prompt = f"""<|im_start|>system
You are VEL, a helpful local AI assistant. Answer only the user's current question. Do not invent follow-up questions or continue the conversation yourself.

Persistent facts about {eid}: {attr_str}
Relevant document context: {context}
Conversation so far:
{history_str}<|im_end|>
<|im_start|>user
{query}<|im_end|>
<|im_start|>assistant
"""

    # Stream response
    response_parts = []
    try:
        print("VEL:", end=" ", flush=True)
        for chunk in main_model(prompt, stream=True,
                                temperature=config.TEMPERATURE,
                                max_tokens=config.MAX_TOKENS,
                                stop=["<|im_end|>", "<|im_start|>", "\nQuestion:", "\nUser:"]):
            token = chunk["choices"][0]["text"]
            print(token, end="", flush=True)
            response_parts.append(token)
        print()
    except Exception as e:  # noqa: BLE001
        log.error("Generation failed: %s", e)
        print(f"\nGeneration failed: {e}")
        return

    full_response = "".join(response_parts).strip()

    # Update history
    _append_history(eid, "user", query)
    _append_history(eid, "assistant", full_response)

    # Extract new facts from exchange
    try:
        exchange = f"User: {query}\nVEL: {full_response}"
        new_facts = auditor.audit_file(exchange, eid, main_model)
        if new_facts:
            core.update_registry(registry, eid, new_facts)
    except Exception as e:  # noqa: BLE001
        log.warning("Fact extraction failed: %s", e)
