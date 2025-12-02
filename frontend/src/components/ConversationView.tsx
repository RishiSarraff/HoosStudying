import React, { useState } from 'react';
import { Box, IconButton } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import ChatMessagesContainer from '../components/ChatMessagesContainer';
import type { ConversationViewProps } from '../types';

const ConversationView: React.FC<ConversationViewProps> = ({
  messages,
  user,
  onSendMessage,
}) => {
  const [inputValue, setInputValue] = useState('');

  const handleSend = () => {
    if (inputValue.trim()) {
      onSendMessage(inputValue.trim());
      setInputValue('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Box
      sx={{
        height: 'calc(100vh - 64px)',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: '#FAFAFA',
      }}
    >
      <ChatMessagesContainer messages={messages} user={user} />

      <Box
        sx={{
          p: 3,
          backgroundColor: '#FFFFFF',
          borderTop: '1px solid #E0E0E0',
        }}
      >
        <Box
          sx={{
            display: 'flex',
            gap: 2,
            alignItems: 'center',
            backgroundColor: '#E8E8F0',
            borderRadius: '24px',
            px: 3,
            py: 1,
          }}
        >
          <input
            type="text"
            placeholder="Enter Text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            style={{
              flex: 1,
              border: 'none',
              outline: 'none',
              backgroundColor: 'transparent',
              fontSize: '0.95rem',
              color: '#212121',
              padding: '8px 0',
            }}
          />
          <IconButton
            onClick={handleSend}
            disabled={!inputValue.trim()}
            sx={{
              color: inputValue.trim() ? '#424242' : '#BDBDBD',
              '&:hover': {
                backgroundColor: 'rgba(0, 0, 0, 0.04)',
              },
            }}
          >
            <SendIcon />
          </IconButton>
        </Box>
      </Box>
    </Box>
  );
};

export default ConversationView;