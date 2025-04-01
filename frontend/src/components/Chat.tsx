import React, { useState, useEffect } from 'react';

interface Message {
  text: string;
  isUser: boolean;
  timestamp: string;
}

function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [isConnecting, setIsConnecting] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Create WebSocket connection
    const socket = new WebSocket('ws://213.210.36.2:8000/api/chat/ws');

    socket.onopen = () => {
      console.log('Connected to WebSocket');
      setIsConnecting(false);
      setMessages(prev => [...prev, {
        text: 'Connected to chat',
        isUser: false,
        timestamp: new Date().toLocaleTimeString()
      }]);
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages(prev => [...prev, {
        text: data.response || data.error,
        isUser: false,
        timestamp: new Date().toLocaleTimeString()
      }]);
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      setError('Error connecting to chat');
      setIsConnecting(false);
    };

    setWs(socket);

    return () => {
      socket.close();
    };
  }, []);

  const sendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || !ws) return;

    ws.send(JSON.stringify({ content: inputMessage }));
    setMessages(prev => [...prev, {
      text: inputMessage,
      isUser: true,
      timestamp: new Date().toLocaleTimeString()
    }]);
    setInputMessage('');
  };

  if (isConnecting) {
    return <div className="connecting">Connecting to chat...</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  return (
    <div className="chat-container">
      <div className="message-container">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`message ${msg.isUser ? 'user-message' : 'bot-message'}`}
          >
            <div>{msg.text}</div>
            <div className="timestamp">{msg.timestamp}</div>
          </div>
        ))}
      </div>
      <form onSubmit={sendMessage} className="input-container">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          className="input-field"
          placeholder="Type a message..."
        />
        <button 
          type="submit"
          className="send-button"
          disabled={!ws || !inputMessage.trim()}
        >
          Send
        </button>
      </form>
    </div>
  );
}

export default Chat; 