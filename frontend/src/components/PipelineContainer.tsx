import type { PipelineContainerProps } from "../types"
import ChatContainer from "./ChatContainer"
import { Box } from "@mui/material";
import PipelineFilesContainer from "./PipelineFilesContainer";


const PipelineContainer: React.FC<PipelineContainerProps> = ({user, pipeline, showChat, refreshKey=0}) => {

    return (
        <Box>
          {showChat ? (
            <ChatContainer 
              user={user} 
              isGeneral={false} 
              pipeline={pipeline}
            />
          ) : (
            <PipelineFilesContainer 
              key={refreshKey}
              user={user} 
              pipeline={pipeline}
            />
          )}
        </Box>
    );
}

export default PipelineContainer