import React from 'react'

export const Sidebar = () => {
    const navItems = [
        { icon: '📊', label: 'Updates', count: 10 },
        { icon: '📅', label: 'Calendar', count: 10 },
        { icon: '👥', label: 'Meetings', active: true },
        { icon: '💡', label: 'Insights' },
        { icon: '📁', label: 'Playlists' },
        { icon: '🎙️', label: 'Record Call' },
    ]

    return (
        <aside className="app-sidebar">
            {/* Logo */}
            <div className="sidebar-logo">
                <span className="logo-icon">🐼</span>
                <span className="logo-text">Panda Studio</span>
            </div>

            {/* Search */}
            <div className="sidebar-search">
                <span className="search-icon">🔍</span>
                <input type="text" placeholder="Search" />
            </div>

            {/* Navigation */}
            <nav className="sidebar-nav">
                {navItems.map((item, idx) => (
                    <div
                        key={idx}
                        className={`nav-item ${item.active ? 'active' : ''}`}
                    >
                        <span className="nav-icon">{item.icon}</span>
                        <span className="nav-label">{item.label}</span>
                        {item.count && <span className="nav-count">{item.count}</span>}
                    </div>
                ))}
            </nav>

            {/* Workspaces */}
            <div className="sidebar-section">
                <div className="section-title">Workspace Library</div>
                <div className="workspace-item">
                    <span className="ws-dot" style={{ background: '#7C3AED' }}></span>
                    <span>Panda Design Agency</span>
                </div>
                <div className="workspace-item">
                    <span className="ws-dot" style={{ background: '#22C55E' }}></span>
                    <span>Panda Admin</span>
                </div>
            </div>

            {/* Bottom Section */}
            <div className="sidebar-footer">
                <div className="nav-item">
                    <span className="nav-icon">⚙️</span>
                    <span className="nav-label">Settings</span>
                </div>
                <div className="nav-item">
                    <span className="nav-icon">👤</span>
                    <span className="nav-label">Invite a friend</span>
                </div>
                <div className="nav-item">
                    <span className="nav-icon">❓</span>
                    <span className="nav-label">Help</span>
                </div>
            </div>

            {/* Assistant Banner */}
            <div className="assistant-banner">
                <span className="assistant-icon">🤖</span>
                <div className="assistant-text">
                    <strong>Hey buddy</strong>
                    <span>Your AI assistant is ready</span>
                </div>
            </div>
        </aside>
    )
}
