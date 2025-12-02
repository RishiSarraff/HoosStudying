import { Box, Typography } from "@mui/material";
import type { PipelineChatContainerComponents } from "../types/index";
import ChatBox from "./ChatBox";
import ConversationContainer from "./ConversationContainer";

const PipelineChatContainer: React.FC<PipelineChatContainerComponents> = ({ user, pipeline }) => {
  console.log(user)
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
        variant="h2"
        sx={{ mb: 4, fontWeight: 700, color: "#212121" }}
      >
        {`Start a New Conversation!`}
      </Typography>
      <ConversationContainer />

      <Box sx={{ width: "100%", maxWidth: 900 }}>
        <ChatBox />
      </Box>
    </Box>
  );
};

export default PipelineChatContainer;
