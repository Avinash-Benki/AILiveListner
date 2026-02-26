import os
import sys
import logging
import time

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.audio_capture import capture_live_audio
from src.stt import WhisperTranscriber
from src.llm import LLMManager
from src.config import CHUNK_DURATION

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # Use the YouTube video shared by the user
    youtube_url = "https://youtu.be/nf465zX3TFc"
    
    logger.info("Initializing Audio + LLM Integration Test (2 minutes)...")
    transcriber = WhisperTranscriber()
    llm_manager = LLMManager()
    
    transcript_buffer = []
    max_chunks = 24  # 24 chunks * 5 seconds = 120 seconds (2 minutes)
    
    logger.info(f"Starting pipeline for URL: {youtube_url}")
    try:
        for i, audio_chunk in enumerate(capture_live_audio(youtube_url, chunk_duration=CHUNK_DURATION)):
            logger.info(f"Processing chunk {i+1}/{max_chunks}...")
            
            # 1. Transcribe
            transcript = transcriber.transcribe_chunk(audio_chunk)
            if transcript:
                transcript_buffer.append(transcript)
                print(f"[{i+1}] Transcript: {transcript}")
            
            # 2. Periodically analyze (every 4 chunks = 20 seconds)
            if (i + 1) % 4 == 0:
                context = " ".join(transcript_buffer[-12:]) # Last ~1 minute of context
                prompt = (
                    f"Provided below is a partial transcript of a finance speech. "
                    f"Please provide a 1-sentence summary of the key points discussed so far.\n\n"
                    f"Transcript: {context}"
                )
                
                logger.info("Triggering LLM analysis...")
                try:
                    analysis = llm_manager.hybrid_call(prompt)
                    print(f"\n--- Analysis (at {i+1} chunks) ---\n{analysis}\n----------------------------\n")
                except Exception as e:
                    logger.error(f"LLM analysis failed: {e}")
            
            # Stop after 2 minutes
            if i >= max_chunks - 1:
                logger.info("2-minute test completed successfully")
                break
                
    except KeyboardInterrupt:
        logger.info("Pipeline stopped by user")
    except Exception as e:
        logger.error(f"Pipeline error: {e}")

if __name__ == "__main__":
    main()
