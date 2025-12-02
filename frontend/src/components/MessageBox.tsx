import React from 'react';
import { Box, Typography } from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import type { MessageBoxProps } from '../types';

const MessageBox: React.FC<MessageBoxProps> = ({ message, userName = "John Doe" }) => {
  const isUser = message.sender_type === 'user';

  if (isUser) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'flex-end',
          mb: 2,
          px: 3,
        }}
      >
        <Box
          sx={{
            maxWidth: '70%',
            minWidth: '200px',
          }}
        >
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              mb: 1,
              justifyContent: 'flex-start',
            }}
          >
            <PersonIcon sx={{ fontSize: 18, color: '#424242' }} />
            <Typography
              variant="body2"
              sx={{
                fontWeight: 600,
                color: '#424242',
                fontSize: '0.875rem',
              }}
            >
              {userName}
            </Typography>
          </Box>
          <Box
            sx={{
              backgroundColor: '#FFFFFF',
              border: '2px solid #424242',
              borderRadius: '16px',
              p: 2,
              wordBreak: 'break-word',
            }}
          >
            <Typography
              variant="body1"
              sx={{
                color: '#212121',
                fontSize: '0.95rem',
                lineHeight: 1.5,
                whiteSpace: 'pre-wrap',
              }}
            >
              {message.message_text}
            </Typography>
          </Box>
        </Box>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'flex-start',
        mb: 2,
        px: 3,
      }}
    >
      <Box
        sx={{
          maxWidth: '70%',
          minWidth: '200px',
        }}
      >
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            mb: 1,
          }}
        >
          <Box
            sx={{
              width: 24,
              height: 24,
              backgroundColor: '#FFFFFF',
              borderRadius: '4px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '1px solid #E0E0E0',
            }}
          >
            <SmartToyIcon sx={{ fontSize: 16}} />
          </Box>
          <Typography
            variant="body2"
            sx={{
              fontWeight: 600,
              color: '#424242',
              fontSize: '0.875rem',
            }}
          >
            {"HoosBot"}
          </Typography>
        </Box>

        <Box
          sx={{
            backgroundColor: '#1976D2',
            borderRadius: '16px',
            p: 2.5,
            wordBreak: 'break-word',
          }}
        >
          <Typography
            variant="body1"
            sx={{
              color: '#FFFFFF',
              fontSize: '0.95rem',
              lineHeight: 1.6,
              whiteSpace: 'pre-wrap',
            }}
          >
            {message.message_text}
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default MessageBox;