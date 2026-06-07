#!/usr/bin/env python3
import logging
import re
from pathlib import Path

import chat
import config
import core
import docs

# Ensure log directory exists
Path(config.LOG_PATH).parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(config.LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logging.getLogger("llama_cpp").setLevel(logging.ERROR)
log = logging.getLogger(__name__)

VALID_EID = re.compile(r"^[a-zA-Z0-9_\-]{1,64}$")
VALID_EXT = {".txt", ".pdf", ".md", ".docx"}

def validate_eid(raw):
    clean = raw.strip()
    if not VALID_EID.match(clean):
        print(f"Invalid name '{clean}'. Letters, numbers, _ or - only.")
        return None
    return clean

def validate_path(raw):
    path = Path(raw.strip())
    if not path.exists():
        print(f"File not found: {path}")
        return None
    if path.suffix.lower() not in VALID_EXT:
        print(f"Unsupported type '{path.suffix}'. Allowed: {', '.join(VALID_EXT)}")
        return None
    return str(path)

def main():
    embed_model, main_model, registry, archive = core.init()
    focus = "user"
    print("VEL ready. Commands: set:<name> | read:<file> | exit\n")
    while True:
        try:
            cmd = input(f"[{focus}] > ").strip()
            if not cmd:
                continue
            if cmd == "exit":
                break
            if cmd.startswith("set:"):
                new = validate_eid(cmd[4:])
                if new:
                    focus = new
            elif cmd.startswith("read:"):
                p = validate_path(cmd[5:])
                if p:
                    docs.read_file(p, focus, embed_model, main_model, registry, archive)
            else:
                chat.chat(cmd, focus, embed_model, main_model, registry, archive)
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit.")
        except Exception as e:
            log.exception("Unhandled error")
            print(f"Something went wrong: {e}")

if __name__ == "__main__":
    main()
