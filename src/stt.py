import numpy as np
import logging
import re
from faster_whisper import WhisperModel
from src.config import WHISPER_MODEL_SIZE, DEVICE, WHISPER_COMPUTE_TYPE

logger = logging.getLogger(__name__)

class WhisperTranscriber:
    def __init__(self, model_size=WHISPER_MODEL_SIZE, device=DEVICE, compute_type=WHISPER_COMPUTE_TYPE):
        logger.info(f"Loading Whisper model: {model_size} on {device} (compute_type={compute_type})")
        try:
            self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model with {compute_type}: {e}")
            logger.info("Falling back to cpu/int8")
            self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
        
        # Sentence boundary accumulator
        self.sentence_buffer = ""
    
    def transcribe_chunk(self, audio_chunk):
        """
        Transcribe a single audio chunk (numpy array).
        Returns the concatenated text from all segments.
        Now includes sentence boundary detection.
        """
        try:
            # faster-whisper expects float32 in range [-1, 1]
            audio_float = audio_chunk.astype(np.float32) / 32768.0
            
            segments, info = self.model.transcribe(audio_float, beam_size=5, language="en")
            
            text = ' '.join(segment.text for segment in segments).strip()
            return text
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            return ""
    
    def transcribe_with_sentence_detection(self, audio_chunk):
        """
        Transcribe with sentence boundary detection.
        Accumulates partial transcripts until a sentence-ending punctuation is found.
        Returns: (complete_sentences: list, pending_text: str)
        """
        raw_text = self.transcribe_chunk(audio_chunk)
        if not raw_text:
            return [], self.sentence_buffer
        
        # Add to buffer
        self.sentence_buffer += " " + raw_text if self.sentence_buffer else raw_text
        
        # Find complete sentences (ending with . ! ?)
        # Pattern matches text ending with sentence punctuation
        sentence_pattern = r'[^.!?]*[.!?]'
        matches = re.findall(sentence_pattern, self.sentence_buffer)
        
        complete_sentences = []
        if matches:
            for match in matches:
                complete_sentences.append(match.strip())
            
            # Remove matched sentences from buffer, keep the remainder
            last_match_end = 0
            for match in matches:
                idx = self.sentence_buffer.find(match, last_match_end)
                if idx != -1:
                    last_match_end = idx + len(match)
            
            self.sentence_buffer = self.sentence_buffer[last_match_end:].strip()
        
        return complete_sentences, self.sentence_buffer
    
    def flush_buffer(self):
        """Force flush any remaining buffered text."""
        remaining = self.sentence_buffer.strip()
        self.sentence_buffer = ""
        return remaining if remaining else None
