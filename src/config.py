import os

from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Paths for models and data
EMBED_MODEL = os.getenv("MODEL_EMBED", "")
MAIN_MODEL = os.getenv("MODEL_MAIN", "")
DB_PATH = "data/memory"
LOG_PATH = "data/vel.log"

# Embedding model settings
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

# Main model settings
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

# Search & generation
TOP_K = 5
TEMPERATURE = 0.1
MAX_TOKENS = 400
