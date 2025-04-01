import React, { useState, useEffect } from 'react';

function Chat() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [ws, setWs] = useState(null);

  useEffect(() => {
    const socket = new WebSocket('ws://213.210.36.2:8000/api/chat/ws');

    socket.onopen = () => {
      console.log('Connected to chat server');
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages(prev => [...prev, data.response || data.error]);
    };

    setWs(socket);

    return () => socket.close();
  }, []);

  const sendMessage = (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || !ws) return;

    ws.send(JSON.stringify({ content: inputMessage }));
    setMessages(prev => [...prev, `You: ${inputMessage}`]);
    setInputMessage('');
  };

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ 
        height: '400px', 
        overflowY: 'auto',
        border: '1px solid #ccc',
        padding: '10px',
        marginBottom: '20px'
      }}>
        {messages.map((msg, index) => (
          <div key={index} style={{ marginBottom: '10px' }}>
            {msg}
          </div>
        ))}
      </div>
      <form onSubmit={sendMessage} style={{ display: 'flex', gap: '10px' }}>
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          style={{ 
            flex: 1,
            padding: '10px',
            border: '1px solid #ccc',
            borderRadius: '4px'
          }}
        />
        <button 
          type="submit"
          style={{
            padding: '10px 20px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Send
        </button>
      </form>
    </div>
  );
}

export default Chat; 