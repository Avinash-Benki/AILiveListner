# 🎙️ AI Live Listener

Real-time AI-powered analysis of live YouTube streams. Captures audio, transcribes speech on-device using Whisper, and runs multi-agent analysis (summarization, topic extraction, impact & sector analysis) via LangGraph — all streamed to a React dashboard over WebSockets.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![React](https://img.shields.io/badge/React-19-61DAFB)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-009688)
![License](https://img.shields.io/badge/License-Apache_2.0-green)

## Architecture

```
YouTube Stream → FFmpeg → Whisper STT → LangGraph Agents → WebSocket → React Dashboard
                                              ↓
                                        Supabase (persistence)
```

**Backend** — Python / FastAPI server with:
- **Audio Capture** — `yt-dlp` + `streamlink` + `ffmpeg` to extract live audio
- **Speech-to-Text** — `faster-whisper` (on-device, base.en model)
- **Voice Activity Detection** — Silero VAD to filter silence
- **LLM Analysis** — Eden AI (cloud) with LM Studio (local) fallback
- **Agent Orchestration** — LangGraph with specialized nodes (summary, topics, impact, sector analysis)
- **Persistence** — Supabase for sessions & events
- **Real-time streaming** — WebSocket broadcast to connected clients

**Frontend** — React 19 + Vite with a timeline-based dashboard showing live transcripts and agent analysis cards.

## Prerequisites

- **Python 3.12+**
- **Node.js 18+** and **npm**
- **FFmpeg** — `brew install ffmpeg`
- **Streamlink** — `pip install streamlink` (or via brew)
- **(Optional)** [LM Studio](https://lmstudio.ai/) — for local LLM fallback
- **(Optional)** [Supabase](https://supabase.com/) project — for session persistence (see [SUPABASE_SETUP.md](SUPABASE_SETUP.md))

## Quick Start

### 1. Clone & setup backend

```bash
git clone https://github.com/Avinash-Benki/AILiveListner.git
cd AILiveListner

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your actual keys
```

### 3. Start the backend

```bash
python -m uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
```

The API server will be available at `http://localhost:8000`.

### 4. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

The dashboard will be available at `http://localhost:5173`.

### 5. Start a stream

Send a POST request to start analyzing a YouTube stream:

```bash
curl -X POST http://localhost:8000/start \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=YOUR_VIDEO_ID"}'
```

Or use the dashboard UI to enter a URL and start the stream.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/start` | Start processing a YouTube stream |
| `POST` | `/stop` | Stop current stream processing |
| `GET` | `/status` | Get current processing status |
| `GET` | `/sessions` | List all past sessions |
| `GET` | `/sessions/{id}` | Get session details with events |
| `WS` | `/ws` | WebSocket for real-time updates |

## Project Structure

```
AILiveListner/
├── src/
│   ├── api.py              # FastAPI server & WebSocket
│   ├── audio_capture.py    # YouTube audio extraction
│   ├── stt.py              # Whisper speech-to-text
│   ├── vad.py              # Voice activity detection
│   ├── llm.py              # LLM manager (Eden AI + LM Studio)
│   ├── orchestrator.py     # Analysis orchestration
│   ├── db.py               # Supabase database manager
│   ├── config.py           # Configuration & env vars
│   └── agents/
│       ├── nodes.py        # LangGraph agent nodes
│       ├── prompts.py      # Agent prompt templates
│       └── state.py        # Agent state definitions
├── frontend/
│   └── src/
│       ├── App.jsx         # Main app component
│       └── components/     # React UI components
├── tests/                  # Test suite
├── docs/                   # Documentation & design docs
├── requirements.txt        # Python dependencies
└── supabase_schema.sql     # Database schema
```

## Environment Variables

See [`.env.example`](.env.example) for all configurable variables.

| Variable | Required | Description |
|----------|----------|-------------|
| `EDEN_AI_API_KEY` | Yes* | Eden AI API key for cloud LLM |
| `SUPABASE_URL` | No | Supabase project URL |
| `SUPABASE_KEY` | No | Supabase anon/public key |

*If not set, the system falls back to local LM Studio.

## License

This project is licensed under the Apache License 2.0 — see the [LICENSE](LICENSE) file for details.
