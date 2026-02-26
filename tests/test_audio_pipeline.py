import os
import sys
import logging
import time

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.audio_capture import capture_live_audio
from src.stt import WhisperTranscriber
from src.config import CHUNK_DURATION

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # Use a reliable short YouTube video for testing
    youtube_url = "https://youtu.be/nf465zX3TFc" #"https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up (reliable test)
    
    logger.info("Initializing transcription pipeline...")
    transcriber = WhisperTranscriber()
    
    logger.info(f"Starting pipeline for URL: {youtube_url}")
    try:
        for i, audio_chunk in enumerate(capture_live_audio(youtube_url, chunk_duration=CHUNK_DURATION)):
            logger.info(f"Processing chunk {i+1}...")
            start_time = time.time()
            
            transcript = transcriber.transcribe_chunk(audio_chunk)
            
            duration = time.time() - start_time
            logger.info(f"Chunk {i+1} Transcription (took {duration:.2f}s):")
            print(f">>> {transcript}")
            
            # Stop after 5 chunks for testing
            if i >= 4:
                logger.info("Test completed (processed 5 chunks)")
                break
                
    except KeyboardInterrupt:
        logger.info("Pipeline stopped by user")
    except Exception as e:
        logger.error(f"Pipeline error: {e}")

if __name__ == "__main__":
    main()
