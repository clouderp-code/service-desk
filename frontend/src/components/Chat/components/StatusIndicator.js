import React from 'react';

function StatusIndicator({ isConnected }) {
  return (
    <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
      <span className="status-dot"></span>
      {isConnected ? 'Connected' : 'Disconnected'}
    </div>
  );
}

export default StatusIndicator; 