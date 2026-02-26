import os
import sys
import logging
import time
import json

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.audio_capture import capture_live_audio
from src.stt import WhisperTranscriber
from src.vad import VADDetector
from src.llm import LLMManager
from src.orchestrator import Orchestrator
from src.config import CHUNK_DURATION

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    youtube_url = "https://youtu.be/nf465zX3TFc"
    
    print("\n" + "="*80)
    print("COMPLETE PIPELINE TEST: Audio → STT → LM Studio → Gemini Grounding")
    print("="*80)
    
    print("\n[STEP 1] Initializing Components...")
    transcriber = WhisperTranscriber()
    vad_detector = VADDetector()
    llm_manager = LLMManager()
    orchestrator = Orchestrator(llm_manager)
    
    transcript_buffer = []
    timestamped_transcripts = []
    max_chunks = 12  # 1 minute
    
    print(f"\n[STEP 2] Processing YouTube Stream: {youtube_url}")
    print("-" * 80)
    
    try:
        voice_chunk_count = 0  # Only count chunks with voice
        for i, audio_chunk in enumerate(capture_live_audio(youtube_url, chunk_duration=CHUNK_DURATION)):
            loop_chunk = i + 1
            now = time.strftime("%H:%M:%S")
            
            # 1. VAD Check (Pre-filter silence)
            if not vad_detector.is_voice(audio_chunk):
                print(f"[{now}] [Chunk {loop_chunk}] Silence/Noiseless detected. Skipping STT.")
                continue
            
            # Increment voice chunk counter only when voice is detected
            voice_chunk_count += 1

            print(f"\n[{now}] [Voice Chunk {voice_chunk_count}/{max_chunks}] Received audio data...")
            
            # 2. Transcribe
            transcript = transcriber.transcribe_chunk(audio_chunk)
            if transcript:
                transcript_buffer.append(transcript)
                timestamped_transcripts.append({
                    "time": now,
                    "text": transcript
                })
                print(f"[{now}] Transcript extracted: \"{transcript}\"")
                
                # 2. Get local summary from LM Studio only after 4 chunks (20 seconds)
                accumulated_text = " ".join(transcript_buffer)
                if len(transcript_buffer) >= 4:  # At least 20 seconds
                    try:
                        local_summary = llm_manager.local_summary(accumulated_text)
                        if local_summary:
                            print(f"  → LM Studio Summary: {local_summary}")
                        else:
                            print(f"  → LM Studio: Insufficient content for summary")
                    except Exception as e:
                        print(f"  → LM Studio Error: {e}")
            
            # 3. Every 6 chunks (30s), check for deep analysis
            if voice_chunk_count % 6 == 0 or voice_chunk_count == max_chunks:
                accumulated_transcript = " ".join(transcript_buffer)
                
                print(f"\n{'='*80}")
                print(f"[ANALYSIS CHECKPOINT] Accumulated {len(transcript_buffer)} chunks")
                print(f"{'='*80}")
                try:
                    # Force analysis at checkpoints to ensure we get a summary and topics
                    result = orchestrator.run_analysis(accumulated_transcript, force=True)
                    if result and result.get('summary'):
                        print("✓ Analysis complete with new insights.")
                        print(f"\n{'-'*40}")
                        print("CURRENT SUMMARY")
                        print(f"{'-'*40}")
                        print(result['summary'])
                        
                        print(f"\n{'-'*40}")
                        print("DEEP ANALYSIS (Eden AI: Topics/Market/Sectors)")
                        print(f"{'-'*40}")
                        print(f"TOPICS: {result.get('topics')}")
                        print(f"MARKET: {result.get('market_impact')}")
                        print(f"SECTORS: {json.dumps(result.get('sector_impacts'), indent=2)}")
                        print(f"{'-'*40}\n")
                    else:
                        print("✗ No new significant insights detected at this checkpoint.")
                except Exception as e:
                    print(f"✗ Analysis Error: {e}")
            
            # Stop after 1 minute
            if voice_chunk_count >= max_chunks:
                print(f"\n[INFO] Reached max chunks ({max_chunks}), stopping...")
                break
            
            # Add flush to ensure output is visible
            sys.stdout.flush()
                
    except KeyboardInterrupt:
        print("\n[STOP] Pipeline stopped by user")
    except Exception as e:
        print(f"\n[ERROR] Pipeline error: {e}")
        print("\n" + "="*80)
        import traceback
        traceback.print_exc()

    print("FINAL PIPELINE REPORT")
    print("="*80)
    
    print("\n[ALL TRANSCRIPTS]")
    print("-" * 40)
    for entry in timestamped_transcripts:
        print(f"[{entry['time']}] {entry['text']}")
        
    print("\n[FINAL SUMMARY LIST]")
    print("-" * 40)
    # Get final summaries from the orchestrator
    final_summaries = orchestrator.summaries
    if final_summaries:
        for i, s in enumerate(final_summaries):
            print(f"{i+1}. {s}")
    else:
        print("No summaries were generated.")

    print("\n" + "="*80)
    print("PIPELINE TEST COMPLETED")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
