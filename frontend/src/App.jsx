import React, { useState, useEffect, useRef, useMemo } from 'react'
import { MiniSidebar } from './components/MiniSidebar'
import { TimelineNav } from './components/TimelineNav'
import { AnalysisCard } from './components/AnalysisCard'
import { CollapsibleSection } from './components/CollapsibleSection'
import './index.css'

function App() {
  const [url, setUrl] = useState('https://youtu.be/a8XQY4Xdf8o')
  const [isRunning, setIsRunning] = useState(false)

  // Data States
  const [transcripts, setTranscripts] = useState([])
  const [insights, setInsights] = useState([]) // Local summaries
  const [analysisHistory, setAnalysisHistory] = useState([]) // All analysis results
  const [latestAnalysis, setLatestAnalysis] = useState(null)
  const [logs, setLogs] = useState([])
  const [audioStatus, setAudioStatus] = useState(null)

  // Navigation / UI State
  const [activeTab, setActiveTab] = useState('transcript')
  const [sidebarView, setSidebarView] = useState('live')
  const [selectedTimelineId, setSelectedTimelineId] = useState(null)
  const [sessionId, setSessionId] = useState(null)
  const [expandedAnalysisId, setExpandedAnalysisId] = useState(null)
  const [pastSessions, setPastSessions] = useState([])
  const [isLoadingHistory, setIsLoadingHistory] = useState(false)

  const ws = useRef(null)
  const scrollRef = useRef(null)

  useEffect(() => {
    connectWebSocket()
    return () => ws.current?.close()
  }, [])

  useEffect(() => {
    if (sidebarView === 'past') {
      fetchSessions()
    }
  }, [sidebarView])

  const fetchSessions = async () => {
    try {
      const resp = await fetch('http://localhost:8000/sessions')
      const data = await resp.json()
      setPastSessions(data.sessions || [])
    } catch (err) {
      console.error('Failed to fetch sessions:', err)
    }
  }

  const loadSession = async (sid) => {
    setIsLoadingHistory(true)
    setSidebarView('live') // Switch to live view to see the data
    try {
      const resp = await fetch(`http://localhost:8000/sessions/${sid}`)
      const data = await resp.json()

      // Process events similar to 'history' socket message
      const events = data.events || []
      const restoredTranscripts = []
      const restoredInsights = []
      const restoredAnalysis = []
      let lastFull = null

      events.forEach(evt => {
        if (evt.type === 'transcript') {
          restoredTranscripts.push({ ...evt.content, id: evt.created_at })
        } else if (evt.type === 'analysis') {
          const content = evt.content
          if (content.local_summary) {
            restoredInsights.push({
              text: content.local_summary,
              id: evt.created_at,
              time: new Date(evt.created_at).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: true, timeZone: 'Asia/Kolkata' })
            })
          }
          restoredAnalysis.push({ ...content, id: evt.created_at, timestamp: evt.created_at })
          lastFull = content
        }
      })

      setSessionId(sid)
      setUrl(data.video_url || url)
      setTranscripts(restoredTranscripts)
      setInsights(restoredInsights)
      setAnalysisHistory(restoredAnalysis)
      if (lastFull) {
        setLatestAnalysis(lastFull)
        if (restoredAnalysis.length > 0) {
          setExpandedAnalysisId(restoredAnalysis[restoredAnalysis.length - 1].id)
        }
      }
    } catch (err) {
      console.error('Failed to load session:', err)
    } finally {
      setIsLoadingHistory(false)
    }
  }

  const formatIST = (dateStr, includeSeconds = false) => {
    if (!dateStr) return "";
    try {
      const date = new Date(dateStr);
      if (isNaN(date.getTime())) return dateStr; // Fallback for plain time strings
      return date.toLocaleTimeString('en-IN', {
        hour: '2-digit',
        minute: '2-digit',
        second: includeSeconds ? '2-digit' : undefined,
        hour12: true,
        timeZone: 'Asia/Kolkata'
      });
    } catch (e) {
      return dateStr;
    }
  }

  const connectWebSocket = () => {
    ws.current = new WebSocket('ws://localhost:8000/ws')
    ws.current.onmessage = (event) => {
      const msg = JSON.parse(event.data)
      handleSocketMessage(msg)
    }
  }

  const handleSocketMessage = (msg) => {
    switch (msg.type) {
      case 'init':
        setIsRunning(msg.data.is_running)
        if (msg.data.session_id) {
          setSessionId(msg.data.session_id)
          console.log('[SESSION] Session ID:', msg.data.session_id)
        }
        break
      case 'history':
        const history = [...msg.data].reverse()
        const restoredTranscripts = []
        const restoredInsights = []
        const restoredAnalysis = []
        let lastFull = null

        history.forEach(evt => {
          if (evt.type === 'transcript') {
            restoredTranscripts.push({ ...evt.content, id: evt.created_at })
          } else if (evt.type === 'analysis') {
            const data = evt.content
            if (data.local_summary) {
              restoredInsights.push({
                text: data.local_summary,
                id: evt.created_at,
                time: evt.created_at
              })
            }
            // Store full analysis
            restoredAnalysis.push({ ...data, id: evt.created_at, timestamp: evt.created_at })
            lastFull = data
          }
        })
        setTranscripts(restoredTranscripts)
        setInsights(restoredInsights)
        setAnalysisHistory(restoredAnalysis)
        if (lastFull) {
          setLatestAnalysis(lastFull)
          // Set the most recent one as expanded
          if (restoredAnalysis.length > 0) {
            setExpandedAnalysisId(restoredAnalysis[restoredAnalysis.length - 1].id)
          }
        }
        break
      case 'transcript':
        setTranscripts(prev => {
          const recentItems = prev.slice(-5)
          const isDuplicate = recentItems.some(item =>
            item.text === msg.data.text && item.time === msg.data.time
          )
          if (isDuplicate) return prev
          return [...prev, { ...msg.data, id: Date.now() }]
        })
        break
      case 'analysis':
        if (msg.data.local_summary) {
          setInsights(prev => [...prev, {
            text: msg.data.local_summary,
            id: Date.now(),
            time: new Date().toISOString()
          }])
        }
        // Add to analysis history
        const newId = Date.now()
        setAnalysisHistory(prev => [...prev, { ...msg.data, id: newId, timestamp: new Date().toISOString() }])
        setLatestAnalysis(msg.data)
        setExpandedAnalysisId(newId)
        break
      case 'status':
        // Handle status updates including session_id
        if (msg.session_id) {
          setSessionId(msg.session_id)
          console.log('[SESSION] Session ID from status:', msg.session_id)
        }
        break
      case 'audio_status':
        setAudioStatus(msg.data)
        break
    }
  }

  // Generate timeline moments from insights or analysis
  const timelineMoments = useMemo(() => {
    // For each full analysis or significant insight, create a moment
    return insights.map(ins => {
      const labelText = ins.text && ins.text.trim().length > 0
        ? (ins.text.length > 60 ? ins.text.slice(0, 60) + '...' : ins.text)
        : 'Analysis';

      return {
        id: ins.id,
        time: formatIST(ins.time),
        label: labelText,
        impact: latestAnalysis?.market_impact?.sentiment || 'Neutral' // Use sentiment from market_impact
      };
    }).reverse(); // Newest first
  }, [insights, latestAnalysis])

  const getYouTubeId = (url) => {
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/
    const match = url.match(regExp)
    return (match && match[2].length === 11) ? match[2] : null
  }

  const handleStart = async () => {
    try {
      await fetch('http://localhost:8000/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, max_minutes: 30 })
      })
      setTranscripts([])
      setInsights([])
      setLatestAnalysis(null)
      setIsRunning(true)
    } catch (err) { console.error(err) }
  }

  const handleStop = async () => {
    await fetch('http://localhost:8000/stop', { method: 'POST' })
    setIsRunning(false)
  }

  const videoId = getYouTubeId(url)

  return (
    <div className="app-wrapper">
      <MiniSidebar activeView={sidebarView} onViewChange={setSidebarView} />

      <div className="main-stage">
        <header className="top-header">
          <div className="header-title-section">
            <h1>Finance Minister Speech – Budget 2026</h1>
            {isRunning && (
              <div className="live-indicator">
                <span className="live-dot"></span>
                Live
              </div>
            )}
            {sessionId && (
              <div className="session-id-badge" title={`Session ID: ${sessionId}`}>
                📋 {sessionId.substring(0, 8)}...
              </div>
            )}
          </div>

          <div className="header-controls">
            <div className="url-input-container">
              <input
                className="url-field"
                value={url}
                onChange={e => setUrl(e.target.value)}
                placeholder="YouTube URL..."
              />
              <button
                className={`action-button ${isRunning ? 'stop' : 'start'}`}
                onClick={isRunning ? handleStop : handleStart}
              >
                {isRunning ? 'Stop' : 'Analyze'}
              </button>
            </div>
          </div>
        </header>

        {sidebarView === 'past' ? (
          <div className="past-sessions-view" style={{ padding: '2rem', overflowY: 'auto', flex: 1 }}>
            <div className="view-header" style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Past Analysis Sessions</h2>
              <button
                className="refresh-button"
                onClick={fetchSessions}
                style={{ padding: '0.5rem 1rem', background: 'var(--primary)', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}
              >
                🔄 Refresh
              </button>
            </div>

            <div className="sessions-table-container" style={{ background: 'var(--surface)', borderRadius: '12px', border: '1px solid var(--border)', overflow: 'hidden' }}>
              <table className="sessions-table" style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead style={{ background: 'var(--surface-base)', borderBottom: '1px solid var(--border)' }}>
                  <tr>
                    <th style={{ padding: '1rem' }}>Session ID</th>
                    <th style={{ padding: '1rem' }}>Video URL</th>
                    <th style={{ padding: '1rem' }}>Created At</th>
                    <th style={{ padding: '1rem' }}>Status</th>
                    <th style={{ padding: '1rem' }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {pastSessions.length === 0 ? (
                    <tr>
                      <td colSpan="5" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>No past sessions found</td>
                    </tr>
                  ) : (
                    pastSessions.map(session => (
                      <tr key={session.id} style={{ borderBottom: '1px solid var(--border)' }}>
                        <td style={{ padding: '1rem' }}><code>{session.id.substring(0, 8)}...</code></td>
                        <td style={{ padding: '1rem', maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{session.video_url}</td>
                        <td style={{ padding: '1rem' }}>{new Date(session.created_at).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })}</td>
                        <td style={{ padding: '1rem' }}>
                          <span className={`status-pill ${session.status}`} style={{ padding: '0.2rem 0.6rem', borderRadius: '4px', fontSize: '0.75rem', background: session.status === 'active' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(0,0,0,0.05)', color: session.status === 'active' ? '#10B981' : 'inherit' }}>
                            {session.status}
                          </span>
                        </td>
                        <td style={{ padding: '1rem' }}>
                          <button
                            className="load-session-btn"
                            onClick={() => loadSession(session.id)}
                            style={{ padding: '0.4rem 0.8rem', background: 'var(--primary)', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '0.875rem' }}
                          >
                            View Analysis
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="column-grid">
            {/* CENTER: Main Content */}
            <main className="primary-content-col">
              <div className="video-sticky-box">
                <div className="video-frame-container">
                  {videoId && (isRunning || isLoadingHistory) ? (
                    <iframe
                      width="100%"
                      height="100%"
                      src={`https://www.youtube.com/embed/${videoId}?autoplay=1&mute=1`}
                      title="YouTube video player"
                      frameBorder="0"
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                      referrerPolicy="strict-origin-when-cross-origin"
                      allowFullScreen
                    />
                  ) : (
                    <div className="video-placeholder">
                      <span className="placeholder-icon">🎬</span>
                      <span>{isLoadingHistory ? 'Loading Session...' : 'Enter URL and click Analyze to start'}</span>
                    </div>
                  )}
                </div>
              </div>

              <div className="tabs-sticky-box">
                <div className="content-tabs">
                  {['transcript', 'summary'].map(t => (
                    <button
                      key={t}
                      className={`tab-trigger ${activeTab === t ? 'active' : ''}`}
                      onClick={() => setActiveTab(t)}
                    >
                      {t === 'transcript' ? 'Transcript' : 'Summary'}
                    </button>
                  ))}
                </div>
              </div>

              <div className="scroll-pane-body">
                {isLoadingHistory ? (
                  <div className="loading-history-overlay" style={{ textAlign: 'center', padding: '3rem' }}>
                    <div className="loader"></div>
                    <p style={{ marginTop: '1rem', color: 'var(--text-muted)' }}>Fetching historical analysis...</p>
                  </div>
                ) : (
                  <>
                    {activeTab === 'transcript' && (
                      <div className="transcript-flow">
                        {transcripts.length === 0 ? (
                          <div className="empty-state">Waiting for data...</div>
                        ) : (
                          [...transcripts].reverse().map((t, idx) => (
                            <div key={idx} className="transcript-message">
                              <div className="msg-time">{formatIST(t.time, true)}</div>
                              <div className="msg-bubble">
                                <span className="msg-speaker">Speaker</span>
                                {t.text}
                              </div>
                            </div>
                          ))
                        )}
                      </div>
                    )}

                    {activeTab === 'summary' && (
                      <div className="summary-view">
                        {insights.length === 0 ? (
                          <div className="empty-state">No summaries yet...</div>
                        ) : (
                          [...insights].reverse().map((ins, i) => (
                            <div key={i} className="summary-card">
                              <div className="summary-time">{formatIST(ins.time)}</div>
                              <div className="summary-text">{ins.text}</div>
                            </div>
                          ))
                        )}
                      </div>
                    )}
                  </>
                )}
              </div>
            </main>

            {/* RIGHT: Timeline Panel with Tabs */}
            <aside className="timeline-sidebar">
              <div className="timeline-tabs">
                <button className="timeline-tab active">Timeline</button>
                <button className="timeline-tab">Comments</button>
                <button className="timeline-tab">Highlighted Clips</button>
              </div>

              <div className="timeline-content">
                {isLoadingHistory ? (
                  <div className="loading-spinner-container" style={{ display: 'flex', justifyContent: 'center', padding: '2rem' }}>
                    <div className="small-loader"></div>
                  </div>
                ) : analysisHistory.length === 0 ? (
                  <div className="empty-state small">AI analysis will appear here</div>
                ) : (
                  <div className="analysis-timeline">
                    {[...analysisHistory].reverse().map((analysis, idx) => {
                      const timestamp = new Date(analysis.timestamp).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true, timeZone: 'Asia/Kolkata' });
                      const topicPills = analysis.topics && analysis.topics.length > 0
                        ? analysis.topics.slice(0, 3)
                        : [];

                      return (
                        <div key={analysis.id} className="analysis-block">
                          <CollapsibleSection
                            title={
                              <div className="analysis-header-content">
                                <span className="analysis-time-tag">{timestamp}</span>
                                <div className="analysis-topics-pills">
                                  {topicPills.map((t, i) => (
                                    <span key={i} className="header-topic-pill">{t.topic}</span>
                                  ))}
                                </div>
                              </div>
                            }
                            isOpen={expandedAnalysisId === analysis.id}
                            onToggle={(isOpen) => setExpandedAnalysisId(isOpen ? analysis.id : null)}
                          >
                            <div className="analysis-inner-content">
                              {/* Local Summary - Quick summary from local LLM */}
                              {analysis.local_summary && (
                                <div className="local-summary-section">
                                  <div className="section-label">Quick Summary</div>
                                  <p className="section-text local-summary-text">{analysis.local_summary}</p>
                                </div>
                              )}

                              {/* Sector Impacts - MOVED TO TOP */}
                              {analysis.sector_impacts && Object.keys(analysis.sector_impacts).length > 0 && (
                                <CollapsibleSection title="Sector Impact">
                                  <div className="sectors-pills-container">
                                    {Object.entries(analysis.sector_impacts).map(([sector, data], i) => (
                                      <div key={i} className={`sector-pill ${data.impact.toLowerCase()}`}>
                                        <span className="sector-name">{sector}</span>
                                        <span className="sector-impact-tag">{data.impact}</span>
                                      </div>
                                    ))}
                                  </div>
                                </CollapsibleSection>
                              )}

                              {/* Market Impact Badge */}
                              {analysis.market_impact && (
                                <CollapsibleSection title="Market Impact">
                                  <div className={`impact-badge-large ${analysis.market_impact.sentiment?.toLowerCase() || 'neutral'}`}>
                                    <div className="impact-sentiment">{analysis.market_impact.sentiment || 'Unknown'}</div>
                                    {analysis.market_impact.reason && (
                                      <div className="impact-reason">{analysis.market_impact.reason}</div>
                                    )}
                                  </div>
                                </CollapsibleSection>
                              )}

                              {/* Topics */}
                              {analysis.topics && analysis.topics.length > 0 && (
                                <CollapsibleSection title="Key Topics">
                                  <div className="topics-list">
                                    {analysis.topics.map((topic, i) => (
                                      <div key={i} className="topic-item">
                                        <div className="topic-name">{topic.topic}</div>
                                        {topic.details && <div className="topic-details">{topic.details}</div>}
                                      </div>
                                    ))}
                                  </div>
                                </CollapsibleSection>
                              )}
                            </div>
                          </CollapsibleSection>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </aside>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
