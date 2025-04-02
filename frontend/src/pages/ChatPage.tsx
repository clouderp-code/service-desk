import React from 'react';
import { Box } from '@mui/material';
import ChatWindow from '../components/Chat/ChatWindow';

const ChatPage: React.FC = () => {
  return (
    <Box sx={{ height: 'calc(100vh - 100px)' }}>
      <ChatWindow />
    </Box>
  );
};

export default ChatPage;
