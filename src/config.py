import os
import torch
from dotenv import load_dotenv

load_dotenv()

# Audio Settings
CHUNK_DURATION = 5  # seconds
SAMPLE_RATE = 16000
CHANNELS = 1

# STT Settings
WHISPER_MODEL_SIZE = "base.en"
WHISPER_COMPUTE_TYPE = "int8"
DEVICE = "cpu"

# LLM Settings
LM_STUDIO_BASE_URL = "http://127.0.0.1:1234/v1"
LM_STUDIO_MODEL = "llama-3.2-3b-instruct"
EDEN_AI_API_KEY = os.getenv("EDEN_AI_API_KEY")


# Buffer Settings
TRANSCRIPT_WINDOW_SIZE = 20  # Number of chunks to keep in context
ANALYSIS_INTERVAL = 3  # Run analysis every N chunks
