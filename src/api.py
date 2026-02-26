import logging
import asyncio
import time
import json
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.audio_capture import capture_live_audio
from src.stt import WhisperTranscriber
from src.vad import VADDetector
from src.llm import LLMManager
from src.orchestrator import Orchestrator
from src.config import CHUNK_DURATION
from src.db import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize DB (will warn if keys missing)
db = DatabaseManager()

app = FastAPI(title="AI Live Listener API")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to socket: {e}")

manager = ConnectionManager()

class StreamRequest(BaseModel):
    url: str
    max_minutes: Optional[int] = 5

class ProcessingState:
    def __init__(self):
        self.is_running = False
        self.current_url = None
        self.task = None

state = ProcessingState()

# Initialize components globally to avoid reloading models on every request
logger.info("Initializing ML Models (Whisper, VAD, LLM)...")
transcriber = WhisperTranscriber()
vad_detector = VADDetector()
llm_manager = LLMManager()
orchestrator = Orchestrator(llm_manager)

async def run_pipeline(url: str, max_chunks: int):
    """The core pipeline loop adapted for async/FastAPI."""
    import queue
    status_queue = queue.Queue()
    
    def audio_status_callback(status: str, message: str):
        """Thread-safe callback to queue status updates from audio capture."""
        status_queue.put((status, message))
    
    async def process_status_updates():
        """Process any queued status updates."""
        while not status_queue.empty():
            try:
                status, message = status_queue.get_nowait()
                await manager.broadcast({"type": "audio_status", "data": {"status": status, "message": message}})
            except queue.Empty:
                break
    
    try:
        state.is_running = True
        state.current_url = url
        # Create DB session
        state.session_id = db.create_session(url)
        if state.session_id:
            logger.info(f"[DB] Session created: {state.session_id}")
        
        voice_chunk_count = 0
        transcript_buffer = []
        
        await manager.broadcast({"type": "status", "data": "connected", "url": url, "session_id": state.session_id})
        
        logger.info("[PIPELINE] Starting main audio processing loop...")
        
        # Infinite retry loop for audio capture resilience
        retry_count = 0
        MAX_RETRIES = 9999  # Effectively infinite for long livestreams
        
        while retry_count < MAX_RETRIES and state.is_running:
            try:
                retry_count += 1
                if retry_count > 1:
                    logger.info(f"[PIPELINE] Restarting audio capture (attempt {retry_count})...")
                    await manager.broadcast({"type": "log", "data": f"Reconnecting to stream (attempt {retry_count})..."})
                
                # Audio capture with status callback for real-time UI updates
                chunk_index = 0
                logger.info(f"[PIPELINE] Entering audio capture for-loop (retry #{retry_count})...")
                
                for audio_chunk in capture_live_audio(url, chunk_duration=CHUNK_DURATION, status_callback=audio_status_callback):
                    try:
                        chunk_index += 1
                        logger.info(f"[PIPELINE] ✓ Received chunk #{chunk_index} from generator")
                        
                        if not state.is_running:
                            logger.info("[PIPELINE] Stop requested. Breaking loop.")
                            break
                        
                        now = datetime.now(timezone.utc).isoformat()
                        
                        # 1. VAD Check
                        logger.debug(f"[PIPELINE] Starting VAD check for chunk {chunk_index}...")
                        is_voice = vad_detector.is_voice(audio_chunk)
                        logger.debug(f"[PIPELINE] VAD result: {'VOICE' if is_voice else 'SILENCE'}")
                        
                        if not is_voice:
                            await manager.broadcast({"type": "log", "data": f"[{now}] Silence detected. Skipping..."})
                            logger.debug(f"[PIPELINE] Continuing to next chunk (silence)")
                            continue
                        
                        voice_chunk_count += 1
                        logger.info(f"[PIPELINE] ✓ Voice detected! Total voice chunks: {voice_chunk_count}")
                        await manager.broadcast({"type": "log", "data": f"[{now}] Voice detected (Chunk {voice_chunk_count})..."})

                        # 2. Transcribe with Sentence Detection
                        logger.info(f"[PIPELINE] Starting transcription for chunk {chunk_index}...")
                        
                        # Use sentence detection to get complete sentences
                        complete_sentences, pending = await asyncio.to_thread(
                            transcriber.transcribe_with_sentence_detection, 
                            audio_chunk
                        )
                        
                        if complete_sentences:
                            logger.info(f"[PIPELINE] ✓ Detected {len(complete_sentences)} complete sentence(s)")
                            
                            # Add all sentences to buffer
                            for sentence in complete_sentences:
                                # Filter out garbage/short sentences
                                clean_text = sentence.strip()
                                # Skip if empty, just punctuation, or very short (<5 chars) without letters
                                if not clean_text or len(clean_text) < 5 or not any(c.isalpha() for c in clean_text):
                                    logger.debug(f"[PIPELINE] Skipping garbage sentence: '{clean_text}'")
                                    continue
                                    
                                transcript_buffer.append(sentence)
                                
                                # Send each complete sentence to UI
                                logger.info(f"[PIPELINE] Broadcasting sentence: '{sentence[:40]}...'")
                                
                                tx_data = {
                                    "time": now,
                                    "text": sentence
                                }
                                
                                # Log to DB
                                if state.session_id:
                                    asyncio.create_task(asyncio.to_thread(db.log_event, state.session_id, "transcript", tx_data))

                                try:
                                    await asyncio.wait_for(
                                        manager.broadcast({
                                            "type": "transcript",
                                            "data": tx_data
                                        }),
                                        timeout=2.0
                                    )
                                    logger.info(f"[PIPELINE] ✓ Sentence broadcast complete")
                                except asyncio.TimeoutError:
                                    logger.warning(f"[PIPELINE] ⚠ Sentence broadcast timed out, continuing...")
                                except Exception as broadcast_error:
                                    logger.error(f"[PIPELINE] Broadcast error: {broadcast_error}")
                        elif pending:
                            logger.debug(f"[PIPELINE] Partial sentence buffered: '{pending[:40]}...'")
                        else:
                            logger.debug(f"[PIPELINE] No text detected in this chunk")
                        
                        # 3. Sliding Window Analysis - Every 12 voice chunks (approx every minute)
                        if voice_chunk_count % 12 == 0:
                            logger.info(f"[PIPELINE] Triggering analysis at voice chunk {voice_chunk_count}")
                            accumulated_transcript = " ".join(transcript_buffer[-30:])
                            
                            # Define background analysis task
                            async def run_background_analysis(chunk_id, text):
                                try:
                                    # Broadcast status
                                    try:
                                        await asyncio.wait_for(manager.broadcast({"type": "status", "data": "analyzing"}), timeout=1.0)
                                    except asyncio.TimeoutError:
                                        pass

                                    logger.info(f"[BACKGROUND] Starting analysis for chunk {chunk_id}...")
                                    # Run analysis in thread pool so it doesn't block event loop
                                    result = await asyncio.to_thread(orchestrator.run_analysis, text)
                                    logger.info(f"[BACKGROUND] Analysis complete for chunk {chunk_id}")
                                    
                                    if result:
                                        analysis_data = {
                                            "local_summary": result.get("local_summary"),
                                            "topics": result.get("topics"),
                                            "market_impact": result.get("market_impact"),
                                            "sector_impacts": result.get("sector_impacts")
                                        }
                                        
                                        # Log what we're sending to frontend
                                        logger.info(f"[API] Broadcasting analysis: "
                                                   f"local_summary={'present' if analysis_data['local_summary'] else 'missing'}, "
                                                   f"{len(analysis_data.get('topics', []))} topics, "
                                                   f"market_impact={'present' if analysis_data['market_impact'] else 'missing'}, "
                                                   f"{len(analysis_data.get('sector_impacts', {}))} sectors")
                                        
                                        if analysis_data.get('topics'):
                                            logger.info(f"[API] Topics: {[t.get('topic') for t in analysis_data['topics']]}")
                                        if analysis_data.get('market_impact'):
                                            logger.info(f"[API] Market Impact: {analysis_data['market_impact']}")
                                        if analysis_data.get('sector_impacts'):
                                            logger.info(f"[API] Sectors: {list(analysis_data['sector_impacts'].keys())}")
                                        
                                        # Log to DB
                                        if state.session_id:
                                            asyncio.create_task(asyncio.to_thread(db.log_event, state.session_id, "analysis", analysis_data))
                                        
                                        try:
                                            await asyncio.wait_for(
                                                manager.broadcast({
                                                    "type": "analysis",
                                                    "data": analysis_data
                                                }),
                                                timeout=2.0
                                            )
                                        except asyncio.TimeoutError:
                                            logger.warning(f"[BACKGROUND] Analysis broadcast timed out")
                                except Exception as e:
                                    logger.error(f"[BACKGROUND] Analysis error: {e}")
                                    try:
                                        await manager.broadcast({"type": "error", "data": str(e)})
                                    except:
                                        pass

                            # Fire and forget!
                            asyncio.create_task(run_background_analysis(voice_chunk_count, accumulated_transcript))

                        if voice_chunk_count >= max_chunks:
                            logger.info("Reached max chunks, stopping.")
                            break
                            
                        # Process any audio status updates from the callback queue
                        await process_status_updates()
                        
                        # Yield control back to event loop
                        logger.debug(f"[PIPELINE] Chunk {chunk_index} complete, yielding to event loop...")
                        await asyncio.sleep(0.01)
                        logger.debug(f"[PIPELINE] Resuming from asyncio.sleep, ready for next chunk...")
                        
                    except Exception as loop_error:
                        logger.error(f"[PIPELINE] Error in loop iteration {chunk_index}: {loop_error}")
                        await manager.broadcast({"type": "error", "data": f"Loop error: {str(loop_error)}"})
                        # Continue to next chunk instead of crashing
                        continue
                
                # If we get here, the generator ended naturally
                if voice_chunk_count >= max_chunks or not state.is_running:
                    logger.info("[PIPELINE] Exiting normally.")
                    break
                    
                # Otherwise, the stream ended - try to reconnect
                logger.warning(f"[PIPELINE] Audio generator ended after {chunk_index} chunks. Reconnecting...")
                await manager.broadcast({"type": "log", "data": "Stream ended. Reconnecting in 2 seconds..."})
                await asyncio.sleep(2)  # Brief pause before retry
                
            except Exception as capture_error:
                logger.error(f"[PIPELINE] Audio capture error on attempt {retry_count}: {capture_error}")
                await manager.broadcast({"type": "error", "data": f"Capture error: {str(capture_error)}"})
                if retry_count < MAX_RETRIES:
                    await asyncio.sleep(2)
                    continue
                else:
                    break

    except Exception as e:
        logger.error(f"Pipeline crashed: {e}")
        await manager.broadcast({"type": "error", "data": f"Pipeline crashed: {str(e)}"})
    finally:
        state.is_running = False
        state.current_url = None
        await manager.broadcast({"type": "status", "data": "stopped"})

@app.post("/start")
async def start_stream(request: StreamRequest, background_tasks: BackgroundTasks):
    if state.is_running:
        return {"status": "error", "message": "A stream is already being processed"}
    
    max_chunks = (request.max_minutes * 60) // CHUNK_DURATION
    background_tasks.add_task(run_pipeline, request.url, max_chunks)
    return {"status": "success", "message": f"Started processing {request.url}"}

@app.post("/stop")
async def stop_stream():
    state.is_running = False
    return {"status": "success", "message": "Stopping stream..."}

@app.get("/status")
async def get_status():
    return {
        "is_running": state.is_running,
        "current_url": state.current_url,
        "summaries_count": len(orchestrator.summaries)
    }

@app.get("/sessions")
async def list_sessions():
    """Get list of all past sessions."""
    sessions = await asyncio.to_thread(db.list_sessions, 50)
    return {"sessions": sessions}

@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get detailed session data with all events."""
    session = await asyncio.to_thread(db.get_session_details, session_id)
    if not session:
        return {"error": "Session not found"}, 404
    return session

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial state
        await websocket.send_json({
            "type": "init",
            "data": {
                "is_running": state.is_running,
                "current_url": state.current_url,
                "summaries": orchestrator.summaries,
                "session_id": getattr(state, "session_id", None)
            }
        })
        
        # Restore history from DB if active session
        if getattr(state, "session_id", None):
            history = await asyncio.to_thread(db.get_recent_events, state.session_id)
            if history:
                logger.info(f"[WS] Sending {len(history)} historical events to client")
                await websocket.send_json({
                    "type": "history",
                    "data": history
                })
        while True:
            # Keep socket open
            data = await websocket.receive_text()
            # We can handle client messages here if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
