import React from "react";
import { Box, TextField, Button, CircularProgress } from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import { sendChatMessage, type ChatResponse } from "../services/chat";
import { auth } from "../firebase";

interface ChatBoxProps {
  pipelineId?: number;
  conversationId?: number;
  onMessageSent?: (response: ChatResponse) => void;
}

export default function ChatBox({
  pipelineId,
  conversationId,
  onMessageSent,
}: ChatBoxProps) {
  const [message, setMessage] = React.useState("");
  const [isLoading, setIsLoading] = React.useState(false);

  const handleSend = async () => {
    if (!message.trim() || isLoading) return;

    setIsLoading(true);
    try {
      const user = auth.currentUser;
      if (!user) {
        console.error("User not authenticated");
        return;
      }

      const token = await user.getIdToken();
      const response = await sendChatMessage(
        token,
        message,
        conversationId,
        pipelineId
      );

      setMessage("");

      if (onMessageSent) {
        onMessageSent(response);
      }
    } catch (error) {
      console.error("Error sending message:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Box
      sx={{
        width: "100%",
        maxWidth: 900,
        backgroundColor: "#9FA8B8",
        borderRadius: 3,
        p: 2,
        display: "flex",
        flexDirection: "column",
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
        disabled={isLoading}
        variant="standard"
        sx={{
          "& .MuiInputBase-root": {
            color: "#FFFFFF",
            fontSize: "1rem",
          },
          "& .MuiInput-underline:before": {
            borderBottom: "none",
          },
          "& .MuiInput-underline:after": {
            borderBottom: "none",
          },
          "& .MuiInput-underline:hover:not(.Mui-disabled):before": {
            borderBottom: "none",
          },
          "& .MuiInputBase-input::placeholder": {
            color: "#E0E0E0",
            opacity: 1,
          },
        }}
      />

      <Box sx={{ display: "flex", justifyContent: "flex-end" }}>
        <Button
          variant="contained"
          onClick={handleSend}
          endIcon={
            isLoading ? (
              <CircularProgress size={20} color="inherit" />
            ) : (
              <SendIcon />
            )
          }
          disabled={!message.trim() || isLoading}
          sx={{
            textTransform: "none",
            fontWeight: 600,
            backgroundColor: "#FFFFFF",
            color: "#9FA8B8",
            "&:hover": {
              backgroundColor: "#F5F5F5",
            },
            "&.Mui-disabled": {
              backgroundColor: "#E0E0E0",
              color: "#BDBDBD",
            },
          }}
        >
          {isLoading ? "Sending..." : "Send"}
        </Button>
      </Box>
    </Box>
  );
}
