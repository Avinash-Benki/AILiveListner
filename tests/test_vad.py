import os
import sys
import numpy as np
import logging

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.vad import VADDetector
from src.audio_capture import capture_live_audio
from src.config import CHUNK_DURATION

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_vad():
    youtube_url = "https://youtu.be/nf465zX3TFc"
    print("\n" + "="*60)
    print("TESTING VAD PRE-FILTERING")
    print("="*60)
    
    detector = VADDetector(threshold=0.4)
    
    print(f"\nProcessing stream: {youtube_url}")
    print("Will monitor 10 chunks and report voice detection...")
    
    count = 0
    voice_count = 0
    
    try:
        for audio_chunk in capture_live_audio(youtube_url, chunk_duration=CHUNK_DURATION):
            count += 1
            has_voice = detector.is_voice(audio_chunk)
            
            status = "VOICE DETECTED" if has_voice else "SILENCE/NOISE"
            print(f"[Chunk {count}] {status}")
            
            if has_voice:
                voice_count += 1
                
            if count >= 10:
                break
    except KeyboardInterrupt:
        pass
    
    print("\n" + "="*60)
    print(f"TEST COMPLETED: {voice_count}/{count} chunks contained voice")
    print("="*60 + "\n")

if __name__ == "__main__":
    test_vad()
