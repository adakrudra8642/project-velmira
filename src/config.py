#!/usr/bin/env python3
import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env
env_path = Path(".env")
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# Base directories
BASE_DIR = (Path(__file__).resolve().parent).parent
DATA_DIR = BASE_DIR / "data"

# Model paths from environment
EMBED_MODEL = os.getenv("MODEL_EMBED", "")
MAIN_MODEL = os.getenv("MODEL_MAIN", "")

# Database and log paths
DB_PATH = DATA_DIR / "memory"
LOG_PATH = DATA_DIR / "vel.log"

# Embedding model configuration
EMBED_CONFIG = {
    "n_ctx": 512,
    "n_batch": 512,
    "n_threads": 8,
    "n_gpu_layers": 0,
    "use_mmap": True,
    "use_mlock": False,
    "verbose": False,
    "logits_all": False,
    "pooling_type": 1,
}

# Main model configuration
MAIN_CONFIG = {
    "n_ctx": 8192,
    "n_batch": 1024,
    "n_threads": 8,
    "n_gpu_layers": 0,
    "use_mmap": True,
    "use_mlock": False,
    "verbose": False,
    "logits_all": False,
}

# Search and generation parameters
TOP_K = 5
TEMPERATURE = 0.1
MAX_TOKENS = 400
