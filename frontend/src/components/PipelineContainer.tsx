import type { PipelineContainerProps } from "../types";
import PipelineChatContainer from "./PipelineChatContainer";
import { Box } from "@mui/material";
import PipelineFilesContainer from "./PipelineFilesContainer";

const PipelineContainer: React.FC<PipelineContainerProps> = ({
  user,
  pipeline,
  showChat,
  refreshKey = 0,
  onDocumentChange,
  onConversationCreated
}) => {
  return (
    <Box>
      {showChat ? (
        <PipelineChatContainer user={user} pipeline={pipeline} onConversationCreated={onConversationCreated}/>
      ) : (
        <PipelineFilesContainer
          key={refreshKey}
          user={user}
          pipeline={pipeline}
          onDocumentChange={onDocumentChange}
        />
      )}
    </Box>
  );
};

export default PipelineContainer;
