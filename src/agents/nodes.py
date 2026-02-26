import json
import logging
from src.agents.state import AgentState
from src.agents.prompts import SUMMARY_PROMPT, TOPICS_PROMPT, IMPACT_PROMPT, SECTORS_PROMPT

logger = logging.getLogger(__name__)

def parse_json_safely(text: str):
    logger.debug(f"Parsing LLM response: {text}")
    try:
        # Remove markdown code blocks if present
        cleaned_text = text.strip()
        if cleaned_text.startswith("```"):
            # Find the first { and last }
            start = cleaned_text.find('{')
            end = cleaned_text.rfind('}')
            if start != -1 and end != -1:
                cleaned_text = cleaned_text[start:end+1]
        
        # Try finding the first { and last } regardless of markdown
        else:
            start = cleaned_text.find('{')
            end = cleaned_text.rfind('}')
            if start != -1 and end != -1:
                cleaned_text = cleaned_text[start:end+1]
        
        return json.loads(cleaned_text)
    except Exception as e:
        logger.error(f"Failed to parse JSON from LLM: {e}")
        logger.error(f"Raw response: {text}")
        return None

def summary_agent(state: AgentState, llm_manager):
    import time
    start = time.time()
    logger.info("Running Summary Agent (Sliding Window)...")
    
    # 1. Prepare windowed transcript (last 3 chunks that triggered analysis)
    windowed_transcript = " ".join(state.get('chunk_history', []))
    
    # 2. Get previous summary for deduplication
    prev_summary = state['summaries'][-1] if state.get('summaries') else None
    
    # 3. Call local_summary with deduplication and word-count validation
    response = llm_manager.local_summary(
        transcript=windowed_transcript, 
        previous_summary=prev_summary
    )
    
    if response:
        state['summary'] = response
        # Prepare combined_summary for downstream nodes (Topics/Impact/Sectors)
        existing = state.get('summaries', [])
        state['combined_summary'] = " ".join(existing + [response])
    else:
        # If None, either word count < 30 or LLM skipped due to duplication/noise
        state['summary'] = None
        state['combined_summary'] = " ".join(state.get('summaries', []))
        
    logger.info(f"Summary Agent finished in {time.time() - start:.2f}s")
    return state

def topics_agent(state: AgentState, llm_manager):
    import time
    start = time.time()
    logger.info("[AGENT] Running Topics Agent via Eden AI...")
    try:
        prompt = TOPICS_PROMPT.format(combined_summary=state.get('combined_summary', ''))
        # Use Eden AI for deep analysis tasks
        response = llm_manager.call_eden_ai(prompt, max_tokens=1024)
        data = parse_json_safely(response)
        if data and 'topics' in data:
            state['topics'] = data['topics']
        else:
            logger.warning("Topics Agent parsed data is invalid.")
            state['errors'].append("Topics Agent: Invalid JSON or data format")
    except Exception as e:
        logger.error(f"Topics Agent execution failed: {e}")
        state['errors'].append(f"Topics Agent: {str(e)}")
    
    logger.info(f"[AGENT] Topics Agent finished in {time.time() - start:.2f}s")
    return state

def impact_agent(state: AgentState, llm_manager):
    import time
    start = time.time()
    logger.info("[AGENT] Running Impact Agent via Eden AI...")
    try:
        prompt = IMPACT_PROMPT.format(combined_summary=state.get('combined_summary', ''))
        # Use Eden AI for deep analysis tasks
        response = llm_manager.call_eden_ai(prompt, max_tokens=1024)
        data = parse_json_safely(response)
        
        if data and 'market_impact' in data:
            state['market_impact'] = data['market_impact']
        else:
            logger.warning("Impact Agent parsed data is invalid.")
            state['errors'].append("Impact Agent: Invalid JSON or data format")
    except Exception as e:
        logger.error(f"Impact Agent execution failed: {e}")
        state['errors'].append(f"Impact Agent: {str(e)}")
    
    logger.info(f"[AGENT] Impact Agent finished in {time.time() - start:.2f}s")
    return state

def sectors_agent(state: AgentState, llm_manager):
    import time
    start = time.time()
    logger.info("[AGENT] Running Sectors Agent via Eden AI...")
    try:
        prompt = SECTORS_PROMPT.format(combined_summary=state.get('combined_summary', ''))
        # Use Eden AI for deep analysis tasks
        response = llm_manager.call_eden_ai(prompt, max_tokens=1024)
        data = parse_json_safely(response)
        
        if data and 'sector_impacts' in data:
            state['sector_impacts'] = data['sector_impacts']
        else:
            logger.warning("Sectors Agent parsed data is invalid.")
            state['errors'].append("Sectors Agent: Invalid JSON or data format")
    except Exception as e:
        logger.error(f"Sectors Agent execution failed: {e}")
        state['errors'].append(f"Sectors Agent: {str(e)}")
    
    logger.info(f"[AGENT] Sectors Agent finished in {time.time() - start:.2f}s")
    return state
