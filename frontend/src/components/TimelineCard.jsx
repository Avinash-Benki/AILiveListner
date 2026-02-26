import React from 'react'

export const TimelineCard = ({ avatar, author, time, text, isAI = false }) => {
    return (
        <div className={`timeline-card ${isAI ? 'ai-card' : ''}`}>
            <div className="card-avatar">
                {avatar || (isAI ? '🤖' : '👤')}
            </div>
            <div className="card-content">
                <div className="card-header">
                    <span className="card-author">{author}</span>
                    <span className="card-time">{time}</span>
                </div>
                <div className="card-text">
                    {text.length > 200 ? (
                        <>
                            {text.slice(0, 200)}...
                            <span className="more-link"> More</span>
                        </>
                    ) : text}
                </div>
            </div>
        </div>
    )
}
