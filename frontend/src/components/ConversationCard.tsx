import type { ConversationCardProps } from "../types/index";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import IconButton from "@mui/material/IconButton";
import DeleteIcon from "@mui/icons-material/Delete";
import Typography from "@mui/material/Typography";
import ChatBubbleOutlineIcon from '@mui/icons-material/ChatBubbleOutline';
import AccessTimeIcon from '@mui/icons-material/AccessTime';

const ConversationCard: React.FC<ConversationCardProps> = ({
  conversation,
  index,
  onDelete,
  isActive = false, 
}) => {
  const formatDate = (date: Date): string => {
    const now = new Date();
    const messageDate = new Date(date);
    const diffMs = now.getTime() - messageDate.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return messageDate.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric' 
    });
  };


  return (
    <Card
      sx={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        p: 2,
        mb: 1,
        width: "100%",
        backgroundColor: isActive ? "#E3F2FD" : "#FFFFFF",
        cursor: "pointer",
        transition: "all 0.2s ease-in-out",
        border: isActive ? "2px solid #1976d2" : "1px solid #E0E0E0",
        borderRadius: 2,
        boxShadow: isActive 
          ? "0 2px 8px rgba(25, 118, 210, 0.15)" 
          : "0 1px 3px rgba(0,0,0,0.05)",
        "&:hover": {
          backgroundColor: isActive ? "#E3F2FD" : "#F5F5F5",
          boxShadow: isActive
            ? "0 4px 12px rgba(25, 118, 210, 0.2)"
            : "0 2px 8px rgba(0,0,0,0.1)",
          transform: "translateY(-1px)",
          borderColor: isActive ? "#1976d2" : "#BDBDBD",
        },
        "&:active": {
          transform: "translateY(0)",
        },
      }}
    >
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          gap: 1.5,
          flex: 1,
          minWidth: 0,
        }}
      >
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            width: 40,
            height: 40,
            borderRadius: "50%",
            backgroundColor: isActive ? "#1976d2" : "#E3F2FD",
            flexShrink: 0,
            transition: "all 0.2s ease-in-out",
          }}
        >
          <ChatBubbleOutlineIcon 
            sx={{ 
              color: isActive ? "#FFFFFF" : "#1976d2", 
              fontSize: 20 
            }} 
          />
        </Box>

        <Box sx={{ flex: 1, minWidth: 0, overflow: "hidden" }}>
          <Typography
            variant="body1"
            component="div"
            sx={{
              fontWeight: isActive ? 600 : 500,
              mb: 0.5,
              fontSize: "0.95rem",
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
              color: isActive ? "#1976d2" : "#212121",
            }}
          >
            {`Conversation #${index + 1}`}
          </Typography>
          <Typography variant="caption" sx={{ color: '#9E9E9E' }}>
            {`${conversation.first_message_content?.substring(0, 40)}...`}
            </Typography>

          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              gap: 0.5,
            }}
          >
            <AccessTimeIcon 
              sx={{ 
                fontSize: 14, 
                color: "#757575" 
              }} 
            />
            <Typography
              variant="caption"
              sx={{
                color: "#757575",
                fontSize: "0.75rem",
              }}
            >
              {formatDate(new Date(conversation.created_at))}
            </Typography>
          </Box>
        </Box>
      </Box>

      <IconButton
        aria-label="delete conversation"
        onClick={(e) => {
          e.stopPropagation();
          if (onDelete) {
            onDelete();
          }
        }}
        sx={{
          backgroundColor: "transparent",
          color: "#9E9E9E",
          flexShrink: 0,
          ml: 1,
          width: 32,
          height: 32,
          opacity: 0,
          transition: "all 0.2s ease-in-out",
          ".MuiCard-root:hover &": {
            opacity: 1,
          },
          "&:hover": {
            backgroundColor: "#FFEBEE",
            color: "#D32F2F",
          },
        }}
      >
        <DeleteIcon sx={{ fontSize: 20 }} />
      </IconButton>
    </Card>
  );
};

export default ConversationCard;
