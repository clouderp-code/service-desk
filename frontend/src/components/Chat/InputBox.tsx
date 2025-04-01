import React, { useState, KeyboardEvent } from 'react';
import { Box, TextField, IconButton } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';

interface InputBoxProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
}

const InputBox: React.FC<InputBoxProps> = ({ onSendMessage, disabled }) => {
  const [message, setMessage] = useState('');

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSendMessage(message);
      setMessage('');
    }
  };

  const handleKeyPress = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
      <Box sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          multiline
          maxRows={4}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          disabled={disabled}
          sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
        />
        <IconButton 
          color="primary" 
          onClick={handleSend} 
          disabled={!message.trim() || disabled}
          sx={{ alignSelf: 'flex-end' }}
        >
          <SendIcon />
        </IconButton>
      </Box>
    </Box>
  );
};

export default InputBox;
