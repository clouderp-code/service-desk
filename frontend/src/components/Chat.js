import React, { useState, useEffect } from 'react';
import './Chat.css';  // Create this file if you want to move styles out

function Chat() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [ws, setWs] = useState(null);
  const [isConnected, setIsConnected] = useState(false);  // Add connection status

  useEffect(() => {
    const socket = new WebSocket('ws://213.210.36.2:8000/api/chat/ws');

    socket.onopen = () => {
      console.log('Connected to chat server');
      setIsConnected(true);  // Track connection status
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const newMessage = {
        text: data.response || data.error,
        timestamp: new Date().toLocaleTimeString(),
        isError: !!data.error,
        isUser: false
      };
      setMessages(prev => [...prev, newMessage]);
    };

    socket.onclose = () => {
      setIsConnected(false);
    };

    setWs(socket);

    return () => socket.close();
  }, []);

  const sendMessage = (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || !ws) return;

    ws.send(JSON.stringify({ content: inputMessage }));
    setMessages(prev => [...prev, {
      text: inputMessage,
      timestamp: new Date().toLocaleTimeString(),
      isUser: true
    }]);
    setInputMessage('');
  };

  return (
    <div className="chat-app">
      <div className="chat-header">
        <h1>AI Assistant</h1>
        <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
          <span className="status-dot"></span>
          {isConnected ? 'Connected' : 'Disconnected'}
        </div>
      </div>
      
      <div className="chat-messages">
        {messages.map((msg, index) => (
          <div 
            key={index} 
            className={`message-wrapper ${msg.isUser ? 'user' : 'assistant'}`}
          >
            <div className={`message ${msg.isError ? 'error' : ''}`}>
              <div className="message-content">{msg.text}</div>
              <div className="message-timestamp">{msg.timestamp}</div>
            </div>
          </div>
        ))}
      </div>

      <form onSubmit={sendMessage} className="chat-input-form">
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
    </div>
  );
}

export default Chat; 