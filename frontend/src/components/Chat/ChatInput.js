import React, { useState } from 'react';

function ChatInput({ onSendMessage, isConnected }) {
  const [inputMessage, setInputMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;
    
    onSendMessage(inputMessage);
    setInputMessage('');
  };

  return (
    <form onSubmit={handleSubmit} className="chat-input-form">
      <input
        type="text"
        value={inputMessage}
        onChange={(e) => setInputMessage(e.target.value)}
        placeholder="Type your message here..."
        className="chat-input"
        disabled={!isConnected}
      />
      <button 
        type="submit"
        className="send-button"
        disabled={!isConnected || !inputMessage.trim()}
      >
        <svg viewBox="0 0 24 24" className="send-icon">
          <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
        </svg>
      </button>
    </form>
  );
}

export default ChatInput; 