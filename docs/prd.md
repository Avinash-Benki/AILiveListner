# Product Requirements Document (PRD) for Real-Time Finance Speech Analysis Agent

## 1. Product Overview
### 1.1 Product Name
Finance Speech Analyzer Agent

### 1.2 Product Description
This is an AI-powered agent designed to process live speeches from a finance minister (e.g., on a finance bill) streamed via YouTube. The agent captures the live audio, performs on-device real-time transcription using local speech-to-text (STT) models, and employs multiple specialized AI agents powered by a hybrid LLM setup to analyze the transcript. The primary LLM is Google's Gemini 2.5 Flash (cloud-based for faster, more accurate responses), with a local Qwen3-32B MLX-optimized model as a backup for offline scenarios or fallback. Multi-agent orchestration is handled via LangGraph (a framework for building agentic workflows, preferred over LangChain for its graph-based structure and state management). These agents handle tasks such as summarization, topic extraction, impact analysis, sector-wise breakdowns, and overall market assessment. The results are displayed in a real-time updating dashboard. The system runs locally on a MacBook Pro with M3 Pro chip where possible, with cloud fallback for the primary LLM, emphasizing privacy, low latency, and reliability.

The agent is built for users interested in financial analysis, such as investors or analysts, to get immediate insights during live budget speeches.

### 1.3 Target Audience
- Individual users (e.g., developers, financial enthusiasts) running on personal MacBooks.
- Focus on macOS (Apple Silicon M3 Pro), but extensible to other platforms.

### 1.4 Key Features
- Live audio capture from YouTube streams.
- On-device STT for real-time transcription.
- Hybrid LLM: Primary - Gemini 2.5 Flash (via API); Backup - Local Qwen3-32B (MLX-optimized).
- Multi-agent orchestration using LangGraph for modular analysis (e.g., summary, topic extraction, impact analysis).
- Interactive dashboard for visualizing transcripts and multi-agent analyses.
- Automatic fallback to local LLM if cloud API fails or offline.

## 2. Goals and Objectives
### 2.1 Business Goals
- Enable real-time financial speech analysis with hybrid cloud-local reliability.
- Provide high-quality, structured outputs through orchestrated multi-agents.
- Serve as a prototype that can be generated entirely by an LLM based on this PRD.

### 2.2 User Goals
- Input: Provide a YouTube live URL for the speech and Gemini API key.
- Output: View live transcript, agent-specific analyses (e.g., summary, topics, impacts), and integrated insights in a dashboard.
- Experience: Low-latency updates (every 5-10 seconds), seamless fallback, easy setup, and customizable prompts for agents.

### 2.3 Success Metrics
- Transcription accuracy: >85% on clear English audio.
- Analysis update frequency: Every 5-30 seconds per agent cycle.
- Fallback success: Automatic switch to local LLM on API errors.
- System runs without crashes on M3 Pro hardware.
- Dashboard refreshes seamlessly with multi-agent outputs.

## 3. Scope
### 3.1 In Scope
- Audio capture from live YouTube URLs using yt-dlp and ffmpeg.
- Chunk-based real-time transcription with faster-whisper (on-device).
- Cumulative transcript buffering for context-aware analysis.
- Hybrid LLM Setup:
  - Primary: Gemini 2.5 Flash (via Google Generative AI API) for all agents.
  - Backup: Qwen3-32B (MLX-optimized, local) triggered on API failures or offline mode.
- Multi-Agent Orchestration via LangGraph:
  - Define agents as nodes in a graph (e.g., Summary Node, Topic Node).
  - Use state management for shared transcript buffer.
  - Sequential or parallel execution (e.g., parallel for independent agents).
  - Agents: Summary, Topic Extraction, Impact Analysis, Sector Analysis.
- Streamlit-based dashboard with live updates (transcript view, agent-specific sections with markdown, lists, and tables).
- Threading for background processing to keep dashboard responsive.
- Basic error handling (e.g., stream interruptions, empty transcripts, LLM parsing failures, API fallbacks).

### 3.2 Out of Scope
- Multi-language support beyond English (though Whisper can handle it with config changes).
- Integration with external APIs beyond Gemini (e.g., real-time stock data; keep fully local except for primary LLM).
- Mobile or web deployment (local run only).
- Advanced UI (e.g., charts; stick to text/tables/lists).
- Audio from sources other than YouTube (e.g., mic or files).
- Other frameworks (focus on LangGraph; LangChain as alternative if needed).

## 4. Functional Requirements
### 4.1 User Flows
1. **Setup**: User installs dependencies, provides Gemini API key (env var), runs the script with a YouTube URL.
2. **Processing**:
   - Capture audio in chunks (5-10 seconds).
   - Transcribe each chunk.
   - Buffer transcripts and trigger LangGraph workflow periodically (e.g., every 2-3 chunks).
   - LangGraph orchestrates agents: Pass buffered transcript through graph nodes (try Gemini first, fallback to Qwen3).
   - Each agent processes independently, outputting structured JSON.
   - Queue integrated results for dashboard.
3. **Display**: Dashboard shows:
   - Live transcript (scrolling text).
   - Agent outputs: Summary (markdown), Topics (list), Overall Impact (markdown), Sector Impacts (table using pandas DataFrame).

### 4.2 Core Components
- **Audio Capture Module**:
  - Use yt-dlp to extract stream URL.
  - ffmpeg to pipe raw audio (16kHz, mono, s16le format).
  - Yield numpy arrays of audio chunks.

- **STT Module**:
  - Load faster-whisper model ("base.en" for speed/accuracy balance).
  - Use MPS device on M3 for acceleration.
  - Transcribe audio chunks to text.
  - Handle partial transcripts.

- **Multi-Agent Orchestration Module**:
  - Framework: LangGraph for graph-based workflow (nodes for agents, edges for flow, state for shared data).
  - LLM Integration:
    - Primary: Gemini 2.5 Flash (via google-generativeai library; API key required).
    - Backup: Qwen3-32B (via mlx-lm; local, MLX-optimized for Apple Silicon).
    - Wrapper function: Try Gemini, catch exceptions (e.g., network errors), fallback to Qwen3.
    - Each agent uses a tailored prompt to generate structured JSON output.
  - Agents (as LangGraph nodes):
    - **Summary Agent**: Prompt: "Summarize the key points from this finance speech transcript: {full_transcript}. Output JSON with 'summary': string."
    - **Topic Extraction Agent**: Prompt: "Extract main topics from this transcript: {full_transcript}. Output JSON with 'topics': list of dicts (e.g., {'topic': 'taxation', 'details': '...'})"
    - **Impact Analysis Agent**: Prompt: "Analyze overall market impact from this transcript: {full_transcript}. Output JSON with 'overall_market_impact': string (e.g., 'Bullish due to...')."
    - **Sector Analysis Agent**: Prompt: "Assess sector-wise impacts: {full_transcript}. Output JSON with 'sector_impacts': dict (e.g., 'IT': {'impact': 'positive', 'reason': '...'})."
  - Buffer full transcript (rolling window of last 10-20 chunks for context).
  - LangGraph Graph: Start -> Parallel/Sequential Agent Nodes -> Compile Outputs -> End.

- **Dashboard Module**:
  - Streamlit app with sections for transcript and each agent's output.
  - Use queue and threading for real-time updates.
  - Display topics as lists/tables, sectors as pandas DataFrame tables.
  - Auto-rerun for refreshes.

### 4.3 Input/Output Specifications
- Input: YouTube URL (string, configurable), Gemini API key (env var).
- Output: Console logs for debugging; dashboard in browser with multi-agent results.

## 5. Non-Functional Requirements
### 5.1 Performance
- Latency: Audio chunk processing <5 seconds; Gemini inference ~1-3 seconds; Qwen3 5-20 seconds on M3 Pro.
- Memory: <20GB usage (for Qwen3 quantization).
- CPU/GPU: Leverage MPS for Whisper and Qwen3.

### 5.2 Security and Privacy
- Local components: No data sent externally except for Gemini API calls.
- Handle API keys securely (env vars).
- Fallback ensures offline functionality.

### 5.3 Reliability
- Graceful handling of stream ends or errors (e.g., retry audio capture).
- LLM Output Validation: Basic JSON parsing with fallbacks.
- Logging: Print transcripts, agent outputs, errors, and fallback triggers to console.

### 5.4 Usability
- Simple run command: `streamlit run agent.py`.
- Configurable: Chunk size, model paths, agent prompts, offline mode via variables.

### 5.5 Compatibility
- macOS (Sonoma+), Apple Silicon M3 Pro.
- Python 3.10+.

## 6. Technical Stack
- **Languages**: Python 3.12.
- **Libraries**:
  - Audio: ffmpeg-python, numpy.
  - STT: faster-whisper (with torch for MPS).
  - LLM Primary: google-generativeai (for Gemini 2.5 Flash).
  - LLM Backup: mlx-lm (for Qwen3-32B MLX-optimized).
  - Orchestration: langgraph, langchain-core (for agents and graphs).
  - Dashboard: streamlit, pandas (for tables).
  - Utils: subprocess, queue, threading, json, os (for env vars).
- **Models**:
  - STT: faster-whisper "base.en".
  - LLM Primary: "gemini-2.5-flash" (API).
  - LLM Backup: Qwen3-32B (e.g., "mlx-community/Qwen3-32B-3bit").
- **Environment Setup**:
  - Homebrew for ffmpeg, yt-dlp.
  - Virtual env for Python deps.
  - Hugging Face cache for Qwen3; Google API key for Gemini.

## 7. Architecture
- **High-Level Design**:
  - Main thread: Streamlit dashboard.
  - Background thread: Audio capture -> STT -> LangGraph workflow (with hybrid LLM) -> Queue results.
  - LangGraph: State includes transcript buffer; nodes call hybrid LLM wrapper.
  - Data Flow: YouTube -> ffmpeg pipe -> Whisper transcribe -> LangGraph Agents (Gemini/Qwen3) -> Streamlit display.

- **Pseudo-Code Outline**:
  ```python
  # agent.py
  import os, subprocess, numpy, torch, json, queue, threading, streamlit as st, pandas as pd
  from faster_whisper import WhisperModel
  from mlx_lm import load, generate
  import google.generativeai as genai
  from langgraph.graph import StateGraph, END
  from typing import TypedDict, List

  # Config
  YOUTUBE_URL = "https://www.youtube.com/watch?v=EXAMPLE_LIVE_ID"
  CHUNK_DURATION = 5
  WHISPER_MODEL_SIZE = "base.en"
  GEMINI_MODEL = "gemini-2.5-flash"
  QWEN_PATH = "mlx-community/Qwen3-32B-3bit"
  GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
  device = "mps" if torch.backends.mps.is_available() else "cpu"
  whisper_model = WhisperModel(WHISPER_MODEL_SIZE, device=device, compute_type="coreml")
  qwen_model, qwen_tokenizer = load(QWEN_PATH)
  genai.configure(api_key=GEMINI_API_KEY)

  transcript_buffer = []
  analysis_queue = queue.Queue()

  class AgentState(TypedDict):
      full_transcript: str
      summary: dict
      topics: dict
      impact: dict
      sectors: dict

  def hybrid_llm_call(prompt):
      try:
          model = genai.GenerativeModel(GEMINI_MODEL)
          response = model.generate_content(prompt)
          return response.text
      except Exception as e:
          print(f"Gemini failed: {e}. Falling back to Qwen3.")
          return generate(qwen_model, qwen_tokenizer, prompt=prompt, max_tokens=512, temp=0.7)

  def run_agent(state, prompt_template, key):
      full_transcript = state['full_transcript']
      prompt = prompt_template.format(full_transcript=full_transcript)
      response = hybrid_llm_call(prompt)
      try:
          json_data = json.loads(response[response.find('{'):response.rfind('}')+1])
          state[key] = json_data
      except:
          state[key] = {"error": response}
      return state

  def summary_agent(state):
      return run_agent(state, "Summarize key points: {full_transcript}. JSON: {{'summary': str}}", "summary")

  def topics_agent(state):
      return run_agent(state, "Extract topics: {full_transcript}. JSON: {{'topics': list of dicts}}", "topics")

  def impact_agent(state):
      return run_agent(state, "Analyze market impact: {full_transcript}. JSON: {{'overall_market_impact': str}}", "impact")

  def sectors_agent(state):
      return run_agent(state, "Assess sectors: {full_transcript}. JSON: {{'sector_impacts': dict}}", "sectors")

  # Build LangGraph
  graph = StateGraph(state_schema=AgentState)
  graph.add_node("summary", summary_agent)
  graph.add_node("topics", topics_agent)
  graph.add_node("impact", impact_agent)
  graph.add_node("sectors", sectors_agent)
  graph.set_entry_point("summary")
  graph.add_edge("summary", "topics")
  graph.add_edge("topics", "impact")
  graph.add_edge("impact", "sectors")
  graph.add_edge("sectors", END)
  app = graph.compile()

  def capture_live_audio(url, chunk_duration):
      # yt-dlp and ffmpeg code

  def transcribe_chunk(audio_chunk):
      # Transcribe code

  def process_stream():
      for chunk in capture_live_audio(YOUTUBE_URL, CHUNK_DURATION):
          transcript = transcribe_chunk(chunk)
          transcript_buffer.append(transcript)
          if len(transcript_buffer) % 3 == 0:
              full_transcript = ' '.join(transcript_buffer[-10:])
              state = {"full_transcript": full_transcript}
              analysis = app.invoke(state)
              analysis_queue.put({'transcript': ' '.join(transcript_buffer), 'analysis': analysis})

  # Start thread and Streamlit UI as before, updating placeholders with analysis['summary'], etc.
  ```

## 8. Assumptions and Constraints
- Assumptions: Speech is primarily English; YouTube stream is public; Gemini API available; Qwen3 handles fallback effectively.
- Constraints: Internet for Gemini; local hardware for Qwen3; API costs for Gemini.
- Risks: API downtime (mitigated by fallback); LLM hallucinations (structured prompts).

## 9. Timeline and Milestones
- As this is for LLM code generation, focus on a single-file prototype (agent.py).
- Testing: Manual with sample YouTube lives and offline simulation.

## 10. Appendix
- References: Conversation history for detailed code snippets and model choices.
- Future Enhancements: Parallel edges in LangGraph for speed, add charts, multi-source input, or export to PDF.