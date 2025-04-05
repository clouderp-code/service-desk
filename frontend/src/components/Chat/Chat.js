import React, { useState, useEffect } from 'react';
import ChatHeader from './ChatHeader';
import ChatMessages from './ChatMessages';
import ChatInput from './ChatInput';
import './Chat.css';

function Chat() {
  const [messages, setMessages] = useState([]);
  const [ws, setWs] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const socket = new WebSocket('ws://213.210.36.2:8000/api/chat/ws');

    socket.onopen = () => {
      console.log('Connected to chat server');
      setIsConnected(true);
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

  const handleSendMessage = (message) => {
    if (!message.trim() || !ws) return;

    ws.send(JSON.stringify({ message: message }));
    setMessages(prev => [...prev, {
      text: message,
      timestamp: new Date().toLocaleTimeString(),
      isUser: true
    }]);
  };

  return (
    <div className="chat-app">
      <ChatHeader isConnected={isConnected} />
      <ChatMessages messages={messages} />
      <ChatInput onSendMessage={handleSendMessage} isConnected={isConnected} />
    </div>
  );
}

export default Chat; 