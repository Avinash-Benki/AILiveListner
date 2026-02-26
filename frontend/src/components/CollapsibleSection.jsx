import React, { useState } from 'react'

export const CollapsibleSection = ({ title, children, isOpen: controlledOpen, onToggle, defaultOpen = true }) => {
    const [internalOpen, setInternalOpen] = useState(defaultOpen)

    const isCurrentlyOpen = controlledOpen !== undefined ? controlledOpen : internalOpen

    const toggle = () => {
        if (onToggle) {
            onToggle(!isCurrentlyOpen)
        } else {
            setInternalOpen(!isCurrentlyOpen)
        }
    }

    return (
        <div className={`timeline-section ${isCurrentlyOpen ? 'is-open' : 'is-closed'}`}>
            <div
                className="section-header"
                onClick={toggle}
            >
                <h3 className="section-title">{title}</h3>
                <span className="collapse-icon">{isCurrentlyOpen ? '▼' : '▶'}</span>
            </div>
            {isCurrentlyOpen && (
                <div className="section-body">
                    {children}
                </div>
            )}
        </div>
    )
}
