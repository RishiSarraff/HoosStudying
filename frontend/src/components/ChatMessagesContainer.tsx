import React, { useEffect, useRef } from 'react';
import { Box } from '@mui/material';
import MessageBox from './MessageBox';
import type { MySQLMessage, MySQLUser } from '../types';

interface ChatMessagesContainerProps {
  messages: MySQLMessage[];
  user: MySQLUser;
}

const ChatMessagesContainer: React.FC<ChatMessagesContainerProps> = ({ 
  messages, 
  user 
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <Box
      sx={{
        flex: 1,
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: '#E0F3FF',
        py: 3,
        minHeight: 0,
      }}
    >
      {messages.length === 0 ? (
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%',
            color: '#9E9E9E',
            fontSize: '0.95rem',
          }}
        >
          {"No messages yet. Start the conversation!"}
        </Box>
      ) : (
        <>
          {messages.map((message) => (
            <MessageBox
              key={message.message_id}
              message={message}
              userName={`${user.first_name} ${user.last_name}`}
            />
          ))}
          <div ref={messagesEndRef} />
        </>
      )}
    </Box>
  );
};

export default ChatMessagesContainer;