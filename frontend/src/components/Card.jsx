import React from 'react';

export default function Card({ children, className = "", hover = true }) {
    return (
        <div className={`glass-panel ${hover ? 'glass-panel-hover' : ''} p-6 ${className}`}>
            {children}
        </div>
    );
}
