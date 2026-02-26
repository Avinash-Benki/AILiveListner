import os
import sys
import logging

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.llm import LLMManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_router():
    manager = LLMManager()
    
    test_sentences = [
        "The government will allocate 50,000 crores for the startup ecosystem specifically in the AI space.",
        "Thank you everyone for joining this live stream today.",
        "We are committed to reducing the fiscal deficit to 4.5% by 2026.",
        "Let me just check my notes for a second.",
        "The agriculture sector will see a 10% increase in credit availability."
    ]
    
    print("\n--- Testing Local Smart Router ---")
    for sentence in test_sentences:
        # Note: This will trigger a model load if not already loaded
        is_worthy = manager.is_insight_worthy(sentence)
        status = "INSIGHT-WORTHY" if is_worthy else "NOISE/SKIP"
        print(f"[{status}] Sentence: {sentence}")

if __name__ == "__main__":
    test_router()
