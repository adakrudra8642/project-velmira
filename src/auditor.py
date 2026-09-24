#!/usr/bin/env python3
import json
import logging
import re

log = logging.getLogger(__name__)

NOISE_KEYS = {"greeting", "vel_response", "user_message", "message", "response", "text"}


def parse_json(text):
    # Try direct JSON parsing
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Fallback to regex extraction
    match = re.search(r"\{.*?\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return None


def filter_facts(facts):
    # Remove noise keys from facts dictionary
    return {k: v for k, v in facts.items() if k.lower() not in NOISE_KEYS}


def extract_facts(content, eid, main_model):
    # Extract persistent facts about entity
    snippet = content[:3000]
    prompt = (
        f"Extract only persistent, reusable facts about {eid} from this text.\n"
        "Good facts: personal details, project details, facts, details, etc.\n"
        "Bad facts: things said in passing, greetings, filler phrases.\n"
        "Return ONLY a flat JSON object. No explanation, no markdown.\n"
        f"Text: {snippet}\n"
        "JSON:"
    )

    # Retry loop for extraction
    for attempt in range(3):
        try:
            raw = main_model(prompt, temperature=0, max_tokens=256)["choices"][0][
                "text"
            ]
            parsed = parse_json(raw)
            if parsed is not None:
                clean = filter_facts(parsed)
                log.info(
                    "Fact extraction succeeded for %s on attempt %d", eid, attempt + 1
                )
                return clean
            log.warning(
                "Fact extraction attempt %d returned no JSON for %s", attempt + 1, eid
            )
        except (KeyError, IndexError, RuntimeError) as err:
            log.error(
                "Fact extraction attempt %d crashed for %s: %s", attempt + 1, eid, err
            )

    log.error("Fact extraction failed all attempts for %s", eid)
    return {}
