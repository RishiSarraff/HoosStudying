import React from 'react';
import { Box, TextField, Button } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';

export default function ChatBox() {
  const [message, setMessage] = React.useState('');

  const handleSend = () => {
    if (message.trim()) {
      console.log('Sending message:', message);
      setMessage('');
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
        width: '100%', 
        maxWidth: 900,
        backgroundColor: '#9FA8B8',
        borderRadius: 3,
        p: 2,
        display: 'flex',
        flexDirection: 'column',
        gap: 1,
      }}
    >
      <TextField
        fullWidth
        multiline
        rows={3}
        placeholder="Enter Text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyPress={handleKeyPress}
        variant="standard"
        sx={{
          '& .MuiInputBase-root': {
            color: '#FFFFFF',
            fontSize: '1rem',
          },
          '& .MuiInput-underline:before': {
            borderBottom: 'none',
          },
          '& .MuiInput-underline:after': {
            borderBottom: 'none',
          },
          '& .MuiInput-underline:hover:not(.Mui-disabled):before': {
            borderBottom: 'none',
          },
          '& .MuiInputBase-input::placeholder': {
            color: '#E0E0E0',
            opacity: 1,
          },
        }}
      />
      
      <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
        <Button
          variant="contained"
          onClick={handleSend}
          endIcon={<SendIcon />}
          disabled={!message.trim()}
          sx={{
            textTransform: 'none',
            fontWeight: 600,
            backgroundColor: '#FFFFFF',
            color: '#9FA8B8',
            '&:hover': {
              backgroundColor: '#F5F5F5',
            },
            '&.Mui-disabled': {
              backgroundColor: '#E0E0E0',
              color: '#BDBDBD',
            },
          }}
        >
          Send
        </Button>
      </Box>
    </Box>
  );
}