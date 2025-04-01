import React from 'react';
import StatusIndicator from './components/StatusIndicator';

function ChatHeader({ isConnected }) {
  return (
    <div className="chat-header">
      <h1>AI Assistant</h1>
      <StatusIndicator isConnected={isConnected} />
    </div>
  );
}

export default ChatHeader; 