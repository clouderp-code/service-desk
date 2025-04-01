import React from 'react';

function Message({ message }) {
  return (
    <div className={`message-wrapper ${message.isUser ? 'user' : 'assistant'}`}>
      <div className={`message ${message.isError ? 'error' : ''}`}>
        <div className="message-content">
          {message.text}
          {message.isTyping && (
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          )}
        </div>
        <div className="message-timestamp">{message.timestamp}</div>
      </div>
    </div>
  );
}

export default Message; 