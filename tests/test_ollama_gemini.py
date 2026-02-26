import os
import sys
import logging

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.llm import LLMManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_ollama_integration():
    print("\n" + "="*60)
    print("TESTING OLLAMA + GEMINI GROUNDING INTEGRATION")
    print("="*60)
    
    manager = LLMManager()
    
    # Test 1: Local summary with Ollama
    print("\n[TEST 1] Local Summary with Ollama")
    sample_text = """
    The government announced a new scheme for clean energy manufacturing. 
    This includes support for solar PV cells, EV batteries, and wind turbines.
    The initiative aims to boost domestic production and reduce imports.
    """
    
    try:
        summary = manager.local_summary(sample_text)
        print(f"Summary: {summary}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Routing decision
    print("\n[TEST 2] Routing Decision")
    test_sentences = [
        "The budget allocates 50,000 crores for renewable energy infrastructure.",
        "Thank you for joining us today.",
    ]
    
    for sentence in test_sentences:
        is_worthy = manager.is_insight_worthy(sentence)
        status = "INSIGHT-WORTHY" if is_worthy else "SKIP"
        print(f"[{status}] {sentence}")
    
    # Test 3: Deep analysis with Gemini grounding (only if significant content)
    print("\n[TEST 3] Deep Analysis with Gemini + Google Search Grounding")
    significant_transcript = """
    The Finance Minister announced a major policy shift in the renewable energy sector.
    The government will provide tax incentives for solar panel manufacturers and 
    increase import duties on Chinese solar cells by 25%. This is expected to 
    significantly impact the domestic manufacturing sector and reduce dependency on imports.
    """
    
    try:
        if manager.is_insight_worthy(significant_transcript):
            print("Content deemed significant. Calling Gemini with grounding...")
            analysis = manager.deep_analysis_with_grounding(significant_transcript)
            print(f"Analysis:\n{analysis}")
        else:
            print("Content not significant enough for deep analysis.")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*60)
    print("TEST COMPLETED")
    print("="*60 + "\n")

if __name__ == "__main__":
    test_ollama_integration()
