import React, { useState } from 'react'

export const MiniSidebar = ({ activeView, onViewChange }) => {
    const [expanded, setExpanded] = useState(false)

    const items = [
        { id: 'live', icon: '🔴', label: 'Live Analysis' },
        { id: 'past', icon: '📁', label: 'Past Sessions' },
    ]

    return (
        <aside
            className={`mini-sidebar ${expanded ? 'expanded' : ''}`}
            onMouseEnter={() => setExpanded(true)}
            onMouseLeave={() => setExpanded(false)}
        >
            <div className="sidebar-brand">
                <span className="brand-icon">🐼</span>
                {expanded && <span className="brand-text">Panda Studio</span>}
            </div>

            <div className="sidebar-nav-list">
                {items.map((item) => (
                    <div
                        key={item.id}
                        className={`sidebar-icon-item ${activeView === item.id ? 'active' : ''}`}
                        onClick={() => onViewChange(item.id)}
                    >
                        <span className="icon">{item.icon}</span>
                        <span className="sidebar-label">{item.label}</span>
                    </div>
                ))}
            </div>
        </aside>
    )
}
