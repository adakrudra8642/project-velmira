import json
import logging
import re

log = logging.getLogger(__name__)

NOISE_KEYS = {"greeting", "vel_response", "user_message", "message", "response", "text"}

def _extract_json(text):
    # Direct parse
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass
    # Fallback regex
    match = re.search(r"\{.*?\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return None

def _filter_noise(facts):
    return {k: v for k, v in facts.items() if k.lower() not in NOISE_KEYS}

def audit_file(content, eid, main_model):
    # Trim and build prompt
    snippet = content[:3000]
    prompt = f"""Extract only persistent, reusable facts about {eid} from this text.
Good facts: name, age, role, location, preferences, goals.
Bad facts: things said in passing, greetings, filler phrases.
Return ONLY a flat JSON object. No explanation, no markdown.
Text: {snippet}
JSON:"""

    # Retry loop
    for attempt in range(3):
        try:
            raw = main_model(prompt, temperature=0, max_tokens=256)["choices"][0]["text"]
            parsed = _extract_json(raw)
            if parsed is not None:
                clean = _filter_noise(parsed)
                log.info("audit_file ok for %s attempt %d: %s", eid, attempt+1, clean)
                return clean
            log.warning("audit_file attempt %d no JSON for %s", attempt+1, eid)
        except Exception as e:  # noqa: BLE001
            log.error("audit_file attempt %d crashed for %s: %s", attempt+1, eid, e)

    log.error("audit_file failed all attempts for %s", eid)
    return {}
