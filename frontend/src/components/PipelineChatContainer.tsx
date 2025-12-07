import React, { useState } from "react";
import { Box, Typography } from "@mui/material";
import type {
  PipelineChatContainerComponents,
  MySQLMessage,
} from "../types/index";
import ChatBox from "./ChatBox";
import ConversationContainer from "./ConversationContainer";
import MessageBox from "./MessageBox";
import type { ChatResponse } from "../services/chat";

const PipelineChatContainer: React.FC<PipelineChatContainerComponents> = ({
  user,
  pipeline,
  onConversationCreated,
}) => {
  const [messages, setMessages] = useState<MySQLMessage[]>([]);
  const [conversationId, setConversationId] = useState<number | undefined>();

  const handleMessageSent = (userText: string, response: ChatResponse) => {
    if (!conversationId) {
      setConversationId(response.conversation_id);
      
      if (onConversationCreated) {
        onConversationCreated(response.conversation_id);
      }
    }

    const userMessage: MySQLMessage = {
      message_id: Date.now(), 
      conversation_id: response.conversation_id,
      sender_type: "user",
      message_text: userText,
      timestamp: new Date(),
    };

    const botMessage: MySQLMessage = {
      message_id: response.message_id,
      conversation_id: response.conversation_id,
      sender_type: "bot",
      message_text: response.response,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage, botMessage]);
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: "#E0F3FF",
        padding: 4,
        margin: 0,
      }}
    >
      <Typography
        variant={messages.length === 0 ? "h2" : "h4"}
        sx={{ 
          mb: 4, 
          fontWeight: messages.length === 0 ? 700 : 600, 
          color: "#212121" 
        }}
      >
        {messages.length === 0 
          ? `Start a New Conversation`
          : pipeline?.pipeline_name || "Chat"}
      </Typography>
  
      <ConversationContainer />
  
      <Box sx={{ width: "100%", maxWidth: 900, mb: 2 }}>
        {messages.map((msg) => (
          <MessageBox
            key={msg.message_id}
            message={msg}
            userName={`${user.first_name} ${user.last_name}`}
          />
        ))}
      </Box>
  
      <Box sx={{ width: "100%", maxWidth: 900 }}>
        <ChatBox
          pipelineId={pipeline?.pipeline_id}
          conversationId={conversationId}
          onMessageSent={handleMessageSent}
        />
      </Box>
    </Box>
  );
};

export default PipelineChatContainer;