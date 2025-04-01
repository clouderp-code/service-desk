import React, { useState, useEffect, useRef } from 'react';
import { Box, Paper, Typography, CircularProgress } from '@mui/material';
import MessageList from './MessageList';
import InputBox from './InputBox';
import { Message } from '../../utils/types';

const ChatWindow: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Connect to WebSocket
    ws.current = new WebSocket('ws://localhost:8000/api/chat/ws');

    ws.current.onopen = () => {
      console.log('Connected to chat server');
    };

    ws.current.onmessage = (event) => {
      const message = JSON.parse(event.data);
      setMessages(prev => [...prev, {
        id: message.id || `msg_${Date.now()}`,
        text: message.text,
        sender: 'ai',
        timestamp: new Date()
      }]);
      setIsLoading(false);
    };

    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsLoading(false);
    };

    return () => {
      ws.current?.close();
    };
  }, []);

  const handleSendMessage = (text: string) => {
    if (!text.trim() || !ws.current) return;

    const newMessage: Message = {
      id: `msg_${Date.now()}`,
      text,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, newMessage]);
    setIsLoading(true);

    ws.current.send(JSON.stringify({ message: text }));
  };

  return (
    <Paper elevation={3} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h6">Chat Assistant</Typography>
      </Box>
      
      <MessageList messages={messages} />
      
      {isLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
          <CircularProgress size={20} />
        </Box>
      )}
      
      <InputBox onSendMessage={handleSendMessage} disabled={isLoading} />
    </Paper>
  );
};

export default ChatWindow;
