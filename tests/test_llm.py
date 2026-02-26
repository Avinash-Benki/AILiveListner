import os
import sys
import logging

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.llm import LLMManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_llm():
    manager = LLMManager()
    test_prompt = "Say 'Hello World' if you're working."
    
    print("\n--- Testing Hybrid LLM Call ---")
    try:
        response = manager.hybrid_call(test_prompt)
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error during hybrid call: {e}")

if __name__ == "__main__":
    test_llm()
