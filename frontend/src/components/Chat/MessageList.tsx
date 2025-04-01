import React, { useEffect, useRef } from 'react';
import { Box, Paper, Typography } from '@mui/material';
import { Message } from '../../utils/types';
import { formatDate } from '../../utils/helpers';

interface MessageListProps {
  messages: Message[];
}

const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <Box sx={{ 
      flexGrow: 1, 
      overflow: 'auto', 
      p: 2,
      display: 'flex',
      flexDirection: 'column',
      gap: 2
    }}>
      {messages.map((message) => (
        <Box
          key={message.id}
          sx={{
            display: 'flex',
            justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start'
          }}
        >
          <Paper
            elevation={1}
            sx={{
              p: 2,
              maxWidth: '70%',
              backgroundColor: message.sender === 'user' ? 'primary.light' : 'grey.100',
              color: message.sender === 'user' ? 'white' : 'text.primary'
            }}
          >
            <Typography variant="body1">{message.text}</Typography>
            <Typography variant="caption" sx={{ display: 'block', mt: 1, opacity: 0.7 }}>
              {formatDate(message.timestamp)}
            </Typography>
          </Paper>
        </Box>
      ))}
      <div ref={messagesEndRef} />
    </Box>
  );
};

export default MessageList;
