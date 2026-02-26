import React from 'react'

export const TimelineNav = ({ items, onSelect, activeId }) => {
    return (
        <aside className="timeline-nav-col">
            <div className="timeline-nav-header">Timeline</div>
            <div className="timeline-scroller">
                {items.length === 0 ? (
                    <div className="p-4 text-xs text-slate-400 italic">No milestones yet...</div>
                ) : (
                    items.map((item) => (
                        <div
                            key={item.id}
                            className={`timeline-nav-item ${activeId === item.id ? 'active' : ''}`}
                            onClick={() => onSelect(item)}
                        >
                            <div className="timeline-dot"></div>
                            <div className="timeline-nav-content">
                                <div className="timeline-meta">
                                    <span className="timeline-time">{item.time}</span>
                                </div>
                                <div className="timeline-label">{item.label}</div>
                                {item.impact && (
                                    <span className={`impact-pill ${item.impact.toLowerCase()}`}>
                                        {item.impact}
                                    </span>
                                )}
                            </div>
                        </div>
                    ))
                )}
            </div>
        </aside>
    )
}
