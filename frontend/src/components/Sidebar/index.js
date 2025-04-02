import React, { useState } from 'react';
import './Sidebar.css';

function Sidebar({ activeComponent, setActiveComponent }) {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const menuItems = [
    { id: 'chat', label: 'Chat', icon: '💬' },
    { id: 'knowledge', label: 'Knowledge Base', icon: '📚' },
    { id: 'email', label: 'Emails', icon: '📧' },
    { id: 'tickets', label: 'Tickets', icon: '🎫' }
  ];

  return (
    <div className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <button 
        className="collapse-button"
        onClick={() => setIsCollapsed(!isCollapsed)}
      >
        {isCollapsed ? '☰' : '✕'}
      </button>

      <div className="sidebar-header">
        <div className="logo">🤖</div>
        {!isCollapsed && <h1>AI Assistant</h1>}
      </div>

      <nav className="sidebar-nav">
        {menuItems.map(item => (
          <button
            key={item.id}
            className={`nav-item ${activeComponent === item.id ? 'active' : ''}`}
            onClick={() => setActiveComponent(item.id)}
          >
            <span className="icon">{item.icon}</span>
            {!isCollapsed && <span className="label">{item.label}</span>}
          </button>
        ))}
      </nav>
    </div>
  );
}

export default Sidebar; 