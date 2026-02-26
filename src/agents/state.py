from typing import TypedDict, List, Dict, Optional

class AgentState(TypedDict):
    # Input
    full_transcript: str
    chunk_history: List[str]  # History of chunks that triggered analysis
    
    # Outputs
    summary: Optional[str]    # Current summary
    summaries: List[str]      # List of all generated summaries
    topics: Optional[List[Dict[str, str]]]
    market_impact: Optional[str]
    sector_impacts: Optional[Dict[str, Dict[str, str]]]
    
    # Metadata
    errors: List[str]
