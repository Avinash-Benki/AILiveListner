import logging
import time
import requests
from openai import OpenAI
from src.config import LM_STUDIO_BASE_URL, LM_STUDIO_MODEL, EDEN_AI_API_KEY

logger = logging.getLogger(__name__)

ROUTER_PROMPT = """
Is this finance speech content significant enough for deep analysis?
Respond with ONLY one word: YES or NO

Content: {text}"""

SUMMARY_PROMPT = """
You are a financial analyst summarizing a speech transcript segment.

TASK: Create a concise 1-2 sentence summary of the key information in the new transcript.

INSTRUCTIONS:
- Extract specific facts, numbers, policy changes, or announcements
- If this information builds on or relates to the previous context, still summarize what was said in THIS segment
- Focus on what is newsworthy or actionable
- Be specific and concrete (avoid vague statements like "discussed various topics")
- If the segment contains meaningful content, ALWAYS provide a summary even if similar topics were mentioned before

Previous context: {previous_summary}

New transcript segment: {transcript}

SUMMARY (1-2 sentences):"""


class LLMManager:
    def __init__(self):
        self.lm_studio_available = False
        
        # Initialize LM Studio client (OpenAI-compatible)
        try:
            self.lm_studio_client = OpenAI(
                base_url=LM_STUDIO_BASE_URL,
                api_key="lm-studio"  # LM Studio doesn't require a real key
            )
            # Test connection
            self.lm_studio_client.models.list()
            self.lm_studio_available = True
            logger.info(f"LM Studio is available at {LM_STUDIO_BASE_URL}, using model: {LM_STUDIO_MODEL}")
        except Exception as e:
            logger.error(f"LM Studio not available: {e}")

    def call_lm_studio(self, prompt, max_tokens=512):
        """Call local LM Studio model for fast, local inference."""
        if not self.lm_studio_available:
            raise RuntimeError("LM Studio not available")
        
        try:
            logger.info(f"LM Studio: Sending request (max_tokens={max_tokens})...")
            start_time = time.time()
            response = self.lm_studio_client.chat.completions.create(
                model=LM_STUDIO_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7,
                timeout=30.0  # 30s timeout
            )
            duration = time.time() - start_time
            logger.info(f"LM Studio: Received response in {duration:.2f}s")
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LM Studio request failed/timed out: {e}")
            raise

    def call_eden_ai(self, prompt, max_tokens=1024):
        """Call Eden AI API for deep analysis agents."""
        if not EDEN_AI_API_KEY:
            logger.warning("EDEN_AI_API_KEY not found. Falling back to local LLM.")
            return self.call_lm_studio(prompt, max_tokens)
            
        url = "https://api.edenai.run/v3/llm/chat/completions"
        headers = {
            "Authorization": f"Bearer {EDEN_AI_API_KEY}",
            "Content-Type": "application/json"
        }
        # Use exact payload from working test_eden.py
        payload = {
            "model": "anthropic/claude-haiku-4-5",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        logger.info(f"Eden AI: Sending request (model={payload['model']})...")
        logger.debug(f"Eden AI: Prompt length: {len(prompt)} chars")
        start_time = time.time()
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            duration = time.time() - start_time
            logger.info(f"Eden AI: Received response in {duration:.2f}s")
            
            # OpenAI-compatible response parsing
            if 'choices' in data and len(data['choices']) > 0:
                content = data['choices'][0]['message']['content']
                logger.info(f"Eden AI: Response length: {len(content)} chars")
                logger.info(f"Eden AI: Response preview: {content[:500]}...")
                return content
            
            logger.warning(f"Eden AI: Unexpected response format: {data}")
            return ""
        except Exception as e:
            logger.error(f"Eden AI request failed: {e}")
            raise

    def call_eden_ai_with_fallback(self, prompt, max_tokens=1024):
        """Wrapper for consistency."""
        return self.call_eden_ai(prompt, max_tokens)

    def local_summary(self, transcript, previous_summary=None, max_tokens=150):
        """Generate a quick local summary using LM Studio."""
        # 1. Word count validation (minimum 30 words)
        word_count = len(transcript.split())
        if word_count < 30:
            logger.info(f"Transcript too short for summary ({word_count} words, need 30)")
            return None
        
        # 2. Prepare prompt with deduplication context
        prev_sum = previous_summary if previous_summary else "No previous summary."
        prompt = SUMMARY_PROMPT.format(transcript=transcript, previous_summary=prev_sum)
        
        logger.info(f"Generating local summary for {word_count}-word transcript...")
        response = self.call_lm_studio(prompt, max_tokens)
        
        if not response:
            logger.warning("Local LLM returned empty response for summary")
            return None
        
        summary = response.strip()
        logger.info(f"Local summary generated ({len(summary)} chars): {summary[:100]}...")
        
        # Return the summary (let orchestrator handle deduplication)
        return summary

    def is_insight_worthy(self, text: str) -> bool:
        """Use local LM Studio to decide if content is significant enough for deep analysis."""
        try:
            logger.info("Routing check via LM Studio...")
            prompt = ROUTER_PROMPT.format(text=text[:500])  # Limit to first 500 chars
            response = self.call_lm_studio(prompt, max_tokens=5).strip().upper()
            logger.info(f"Router decision: {response}")
            return "YES" in response
        except Exception as e:
            logger.error(f"Routing check failed: {e}. Defaulting to YES.")
            return True

    def deep_analysis(self, transcript):
        """Perform deep analysis using Eden AI."""
        prompt = f"""
Analyze this finance speech transcript and provide insights as a financial analyst.
Output ONLY a JSON object with this structure:
{{
  "topics": [list of main topics discussed],
  "market_impact": "overall market sentiment and reasoning",
  "sector_impacts": {{"Sector": {{"impact": "Positive/Negative/Neutral", "reason": "brief reason"}}, ...}}
}}

Transcript:
{transcript}
"""
        return self.call_eden_ai(prompt, max_tokens=2048)
