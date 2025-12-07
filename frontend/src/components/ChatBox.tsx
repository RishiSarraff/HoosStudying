import React, { useState } from 'react';
import { Box, IconButton, CircularProgress } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import { sendChatMessage } from '../services/chat';
import { getCurrentToken } from '../services/auth';
import type { ChatResponse } from '../services/chat';

interface ChatBoxProps {
  pipelineId?: number;
  conversationId?: number;
  onMessageSent: (userText: string, response: ChatResponse) => void;
}

const ChatBox: React.FC<ChatBoxProps> = ({
  pipelineId,
  conversationId,
  onMessageSent,
}) => {
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!inputValue.trim() || loading) return;

    const messageText = inputValue.trim();
    setInputValue('');
    setLoading(true);

    try {
      const token = await getCurrentToken();
      if (!token) {
        throw new Error('No authentication token');
      }

      const response = await sendChatMessage(
        token,
        messageText,
        conversationId,
        pipelineId
      );

      onMessageSent(messageText, response);
    } catch (error) {
      console.error('Error sending message:', error);
      // You might want to show an error alert here
      setInputValue(messageText); // Restore the message on error
    } finally {
      setLoading(false);
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
        onKeyPress={handleKeyPress}
        disabled={loading}
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
        disabled={!inputValue.trim() || loading}
        sx={{
          color: inputValue.trim() && !loading ? '#424242' : '#BDBDBD',
          '&:hover': {
            backgroundColor: 'rgba(0, 0, 0, 0.04)',
          },
        }}
      >
        {loading ? <CircularProgress size={24} /> : <SendIcon />}
      </IconButton>
    </Box>
  );
};

export default ChatBox;