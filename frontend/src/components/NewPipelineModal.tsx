import type { NewPipelineModalProps } from "../types/index";
import TextField from "@mui/material/TextField";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
} from "@mui/material";
import { useState } from "react";

const NewPipelineModal: React.FC<NewPipelineModalProps> = ({
  user_id,
  open,
  onClose,
  onSubmit,
  isEditMode,
  pipeline
}) => {
  const [pipelineName, setPipelineName] = useState<string>((isEditMode && pipeline) ? pipeline.pipeline_name : "");
  const [pipelineDescription, setPipelineDescription] = useState<string>((isEditMode && pipeline) ? pipeline.description : "");

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>{isEditMode ? "Edit Pipeline" : "Create New Pipeline"}</DialogTitle>
      <DialogContent>
        <TextField
          fullWidth
          required
          label="Pipeline Name"
          value={pipelineName}
          onChange={(e) => setPipelineName(e.target.value)}
          error={pipelineName.length > 50}
          helperText={
            pipelineName.length > 50 ? "Pipeline Name is too long" : ""
          }
          margin="normal"
        />
        <TextField
          fullWidth
          label="Pipeline Description"
          required
          multiline
          rows={4}
          value={pipelineDescription}
          onChange={(e) => setPipelineDescription(e.target.value)}
          margin="normal"
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>{"Cancel"}</Button>
        <Button
          variant="contained"
          onClick={() =>
            onSubmit({ pipelineName, pipelineDescription, user_id })
          }
          disabled={(isEditMode && pipeline && pipeline.pipeline_name == pipelineName.trim() && pipeline.description == pipelineDescription.trim())}
        >
          {isEditMode ? "Edit" : "Create"}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default NewPipelineModal;
