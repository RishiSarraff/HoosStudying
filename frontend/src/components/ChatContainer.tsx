import { Box, Typography } from "@mui/material"
import type { ChatContainerComponents } from "../types/index"
import ChatBox from "./ChatBox"
import ConversationContainer from "./ConversationContainer"

const ChatContainer: React.FC<ChatContainerComponents> = ({user}) => {

    return(
        <Box
            sx={{
                minHeight: "100vh",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                backgroundColor: "#f5f5f5",
                padding: 4,
            }}
            >
            <Typography variant="h2" sx={{ mb: 4, fontWeight: 600 }}>
                Welcome, {user.first_name}!
            </Typography>
            <ConversationContainer/>

            <Box sx={{ width: "100%" }}>
                <ChatBox />
            </Box>
            
            
        </Box>
    )
}

export default ChatContainer