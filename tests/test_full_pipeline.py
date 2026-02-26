import os
import sys
import logging
import time
import json

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.audio_capture import capture_live_audio
from src.stt import WhisperTranscriber
from src.llm import LLMManager
from src.orchestrator import Orchestrator
from src.config import CHUNK_DURATION

# Configure logging to be less verbose for the test output
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# Keep our module logs at INFO
logging.getLogger("src.audio_capture").setLevel(logging.INFO)
logging.getLogger("src.stt").setLevel(logging.INFO)
logging.getLogger("src.llm").setLevel(logging.INFO)
logging.getLogger("src.orchestrator").setLevel(logging.INFO)

logger = logging.getLogger(__name__)

def main():
    youtube_url = "https://youtu.be/nf465zX3TFc"
    
    print("\n" + "="*80)
    print("FULL PIPELINE INTEGRATION TEST (1 MINUTE)")
    print("="*80)
    
    print("\n[STEP 1] Initializing Components...")
    transcriber = WhisperTranscriber()
    llm_manager = LLMManager()
    orchestrator = Orchestrator(llm_manager)
    
    transcript_buffer = []
    max_chunks = 12  # 12 chunks * 5 seconds = 60 seconds (1 minute)
    
    print(f"\n[STEP 2] Starting Stream Processing for {youtube_url}...")
    try:
        for i, audio_chunk in enumerate(capture_live_audio(youtube_url, chunk_duration=CHUNK_DURATION)):
            chunk_num = i + 1
            print(f"\n--- Chunk {chunk_num}/{max_chunks} ---")
            
            # 1. Transcribe
            transcript = transcriber.transcribe_chunk(audio_chunk)
            if transcript:
                transcript_buffer.append(transcript)
                print(f"Transcript: \"{transcript}\"")
            
            # 2. Analyze every 4 chunks (20s) OR at the very end
            if chunk_num % 4 == 0 or chunk_num == max_chunks:
                accumulated_transcript = " ".join(transcript_buffer)
                print(f"\n[ANALYSIS] Triggering Multi-Agent Analysis (Context: {len(transcript_buffer)} chunks)...")
                
                # We use force=True for the test to ensure we see outputs even if router is picky
                # but in real usage we'd let the router decide.
                result = orchestrator.run_analysis(accumulated_transcript, force=True)
                
                if result:
                    print("\n" + "-"*40)
                    print("MULTI-AGENT INSIGHTS")
                    print("-"*40)
                    print(f"SUMMARY:\n{result.get('summary')}")
                    print(f"\nTOPICS:\n{json.dumps(result.get('topics'), indent=2)}")
                    print(f"\nMARKET IMPACT:\n{result.get('market_impact')}")
                    print(f"\nSECTOR IMPACTS:\n{json.dumps(result.get('sector_impacts'), indent=2)}")
                    if result.get('errors'):
                        print(f"\nERRORS: {result.get('errors')}")
                    print("-"*40)
            
            # Stop after 1 minute
            if i >= max_chunks - 1:
                break
                
    except KeyboardInterrupt:
        print("\n[STOP] Pipeline stopped by user")
    except Exception as e:
        print(f"\n[ERROR] Pipeline error: {e}")

    print("\n" + "="*80)
    print("TEST COMPLETED")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
