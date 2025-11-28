import { Button } from "@mui/material";
import ChatBubbleIcon from '@mui/icons-material/ChatBubble';
import type { ChatButtonProps } from "../types";


const ChatButton: React.FC<ChatButtonProps> = ({ onClick, isActive = false }) => {
  return (
    <Button
      variant={isActive ? "contained" : "outlined"}
      startIcon={<ChatBubbleIcon />}
      onClick={onClick}
      sx={{
        textTransform: 'none',
        backgroundColor: isActive ? '#1976D2' : 'transparent',
        color: isActive ? '#FFFFFF' : '#212121',
        borderColor: '#212121',
        '&:hover': {
          backgroundColor: isActive ? '#1565C0' : 'rgba(0, 0, 0, 0.04)',
        }
      }}
    >
      Chat
    </Button>
  );
};

export default ChatButton;