import torch
import numpy as np
import logging
from src.config import SAMPLE_RATE

logger = logging.getLogger(__name__)

class VADDetector:
    def __init__(self, threshold=0.5):
        """
        Initialize Silero VAD detector.
        """
        logger.info("Initializing Silero VAD detector...")
        self.model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                                          model='silero_vad',
                                          force_reload=False,
                                          onnx=True)
        (self.get_speech_timestamps, self.save_audio, self.read_audio, self.VADIterator, self.collect_chunks) = utils
        self.threshold = threshold
        logger.info("Silero VAD detector initialized.")

    def is_voice(self, audio_data: np.ndarray) -> bool:
        """
        Detect if the audio chunk contains voice.
        Expects 16kHz mono audio.
        """
        try:
            # Normalize to [-1.0, 1.0] if it's int16
            if audio_data.dtype == np.int16:
                audio_float = audio_data.astype(np.float32) / 32768.0
            else:
                audio_float = audio_data
                
            tensor_audio = torch.from_numpy(audio_float)
            
            # Use get_speech_timestamps for handling larger chunks
            # It returns a list of dictionaries with start/end timestamps
            speech_timestamps = self.get_speech_timestamps(
                tensor_audio, 
                self.model, 
                sampling_rate=SAMPLE_RATE,
                threshold=self.threshold
            )
            
            is_speech = len(speech_timestamps) > 0
            logger.debug(f"VAD detected {len(speech_timestamps)} speech segments (Is Speech: {is_speech})")
            
            return is_speech
        except Exception as e:
            logger.error(f"VAD detection failed: {e}")
            return True # Fallback to sending if VAD fails
