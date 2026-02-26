import os
import sys
import logging
import json

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.orchestrator import Orchestrator
from src.llm import LLMManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_orchestration():
    # Sample transcript from a typical finance speech
    sample_transcript = """
    We are announcing a new mission for green energy. The government will provide 20,000 crores for 
    solar power infrastructure. This will significantly benefit the power and manufacturing sectors. 
    However, we are increasing the surcharge on high-income individuals to fund these initiatives. 
    The market might react cautiously to the fiscal deficit targets, but the long-term outlook remains positive.
    The IT sector will continue to get support through tax incentives for startups.
    """

    logger.info("Initializing Orchestrator with Hybrid LLM...")
    llm_manager = LLMManager()
    orchestrator = Orchestrator(llm_manager)

    logger.info("Running full multi-agent analysis test...")
    result = orchestrator.run_analysis(sample_transcript)

    print("\n" + "="*50)
    print("ANALYSIS RESULTS")
    print("="*50)
    print(f"Summary: {result.get('summary')}")
    print(f"\nTopics: {json.dumps(result.get('topics'), indent=2)}")
    print(f"\nMarket Impact: {result.get('market_impact')}")
    print(f"\nSector Impacts: {json.dumps(result.get('sector_impacts'), indent=2)}")
    print(f"\nErrors: {result.get('errors')}")
    print("="*50)

if __name__ == "__main__":
    test_orchestration()
