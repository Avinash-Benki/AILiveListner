"""
Simple Orchestrator - No LangGraph, just clean Python functions.
Manages the multi-agent analysis pipeline.
"""
import logging
from typing import Dict, List, Optional

from src.llm import LLMManager
from src.llm import LLMManager

logger = logging.getLogger(__name__)


def parse_json_safely(text: str) -> Optional[dict]:
    """Parse JSON from LLM response, handling markdown code blocks."""
    import json
    try:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            start = cleaned.find('{')
            end = cleaned.rfind('}')
            if start != -1 and end != -1:
                cleaned = cleaned[start:end+1]
        else:
            start = cleaned.find('{')
            end = cleaned.rfind('}')
            if start != -1 and end != -1:
                cleaned = cleaned[start:end+1]
        return json.loads(cleaned)
    except Exception as e:
        logger.error(f"JSON parse failed: {e}")
        return None


class Orchestrator:
    """Simple sequential orchestrator for the analysis pipeline."""
    
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager
        # Session state
        self.chunk_history: List[str] = []
        self.summaries: List[str] = []
    def _is_duplicate(self, new_summary: str) -> bool:
        """Check if summary is too similar to existing ones."""
        if not new_summary or len(new_summary) < 20:
            logger.info(f"Summary rejected: too short ({len(new_summary) if new_summary else 0} chars)")
            return True
        
        # Check for very generic/empty responses
        generic_phrases = [
            "no new information",
            "no significant",
            "nothing new",
            "same as before",
            "previously mentioned"
        ]
        summary_lower = new_summary.lower()
        for phrase in generic_phrases:
            if phrase in summary_lower:
                logger.info(f"Summary rejected: contains generic phrase '{phrase}'")
                return True
        
        # Check similarity with recent summaries (last 3)
        recent_summaries = self.summaries[-3:] if len(self.summaries) > 3 else self.summaries
        for idx, s in enumerate(recent_summaries):
            # Calculate simple word overlap
            new_words = set(new_summary.lower().split())
            old_words = set(s.lower().split())
            
            if len(new_words) == 0:
                continue
                
            overlap = len(new_words & old_words) / len(new_words)
            
            # If more than 80% of words overlap, consider it duplicate
            if overlap > 0.8:
                logger.info(f"Summary rejected: {overlap*100:.0f}% word overlap with summary #{len(self.summaries)-len(recent_summaries)+idx+1}")
                return True
        
        return False
    
    def _run_summary(self, transcript: str) -> Optional[str]:
        """Run local summary generation."""
        prev_summary = self.summaries[-1] if self.summaries else None
        return self.llm_manager.local_summary(transcript, prev_summary)

    
    def _run_combined(self, transcript: str, local_summary: str = None) -> Dict:
        """Run all analysis in a single call using Eden AI."""
        from src.agents.prompts import COMBINED_ANALYSIS_PROMPT
        
        # Default empty result
        empty_result = {
            "topics": [],
            "market_impact": None,
            "sector_impacts": {},
            "errors": []
        }
        
        try:
            # Use local summary if available, otherwise use a placeholder
            summary_text = local_summary if local_summary else "No local summary available."
            prompt = COMBINED_ANALYSIS_PROMPT.format(
                local_summary=summary_text,
                transcript=transcript
            )
            
            logger.info("[EDEN AI] Calling Eden AI for combined analysis...")
            response = self.llm_manager.call_eden_ai(prompt, max_tokens=3000)
            logger.info(f"[EDEN AI] Raw response received: {response}...")
            
            data = parse_json_safely(response)
            
            if not data:
                logger.warning("[EDEN AI] Failed to parse JSON from response")
                logger.warning(f"[EDEN AI] Full response: {response}")
                return empty_result
            
            logger.info(f"[EDEN AI] Parsed JSON keys: {list(data.keys())}")
            logger.info(f"[EDEN AI] Topics count: {len(data.get('topics', []))}")
            logger.info(f"[EDEN AI] Market impact: {data.get('market_impact')}")
            logger.info(f"[EDEN AI] Sector impacts count: {len(data.get('sector_impacts', {}))}")
            
            result = {
                "topics": data.get("topics", []),
                "market_impact": data.get("market_impact"),
                "sector_impacts": data.get("sector_impacts", {}),
                "errors": []
            }
            
            logger.info(f"[EDEN AI] Returning result with {len(result['topics'])} topics, "
                       f"market_impact={'present' if result['market_impact'] else 'missing'}, "
                       f"{len(result['sector_impacts'])} sectors")
            
            return result
        except Exception as e:
            logger.error(f"[EDEN AI] Combined analysis failed: {e}", exc_info=True)
            return empty_result

    def run_analysis(self, transcript: str, force: bool = False) -> Dict:
        """
        Run the complete analysis pipeline.
        Returns both local summary and deep analysis result.
        """
        # 1. Update history
        self.chunk_history.append(transcript)
        
        # Check if transcript is substantive enough
        if len(transcript.split()) < 15:
            logger.info("Transcript too short for analysis.")
            return None

        # 2. Run Local Summary first (for the timeline)
        logger.info("[STEP 1] Running Local Summary...")
        local_summary = self._run_summary(transcript)
        
        if not local_summary or self._is_duplicate(local_summary):
            logger.info("No significant new info for summary. Skipping deep analysis.")
            return None

        self.summaries.append(local_summary)
        logger.info(f"Local summary added: {local_summary[:50]}...")

        # 3. Run Single Shot Deep Analysis (Eden AI) for the sidebar
        logger.info("[STEP 2] Running Combined Deep Analysis...")
        deep_result = self._run_combined(transcript, local_summary)
        
        # Merge results
        result = {
            "local_summary": local_summary,
            "topics": deep_result.get("topics", []),
            "market_impact": deep_result.get("market_impact"),
            "sector_impacts": deep_result.get("sector_impacts", {}),
            "errors": deep_result.get("errors", [])
        }
        
        return result
