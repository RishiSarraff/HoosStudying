import type { MySQLTag, NewPipelineModalProps } from "../types/index";
import TextField from "@mui/material/TextField";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  FormControl,
  FormHelperText,
  MenuItem,
  Select,
  Box,
  InputLabel,
} from "@mui/material";
import { useState, useEffect } from "react";
import { getSystemTags } from "../services/pipeline";
import { getCurrentToken } from "../services/auth";

const NewPipelineModal: React.FC<NewPipelineModalProps> = ({
  user_id,
  open,
  onClose,
  onSubmit,
  isEditMode,
  pipeline
}) => {
  const [pipelineName, setPipelineName] = useState<string>(
    (isEditMode && pipeline) ? pipeline.pipeline_name : ""
  );
  const [pipelineDescription, setPipelineDescription] = useState<string>(
    (isEditMode && pipeline) ? pipeline.description : ""
  );
  const [systemTags, setSystemTags] = useState<MySQLTag[]>([]);
  const [selectedSystemTagId, setSelectedSystemTagId] = useState<number | ''>('');
  const [originalSystemTagId, setOriginalSystemTagId] = useState<number | ''>('');

  useEffect(() => {
    const loadSystemTags = async () => {
      try {
        const token = await getCurrentToken();
        if (token) {
          const retrievedSystemTags = await getSystemTags(token);
          setSystemTags(retrievedSystemTags);

          if (isEditMode && pipeline && pipeline.pipeline_tags && pipeline.pipeline_tags.length > 0) {
            const systemTag = pipeline.pipeline_tags.find(t => t.tag_type === 'system');
            if (systemTag) {
              setOriginalSystemTagId(systemTag.tag_id);
              setSelectedSystemTagId(systemTag.tag_id);
            }
          }
        }
      } catch (error) {
        console.error("Could not load System Tags: ", error);
      }
    };

    if (open) {
      loadSystemTags();
    }
  }, [open, isEditMode, pipeline]);

  const hasChanges = () => {
    if (!isEditMode || !pipeline) return true;

    const nameChanged = pipeline.pipeline_name !== pipelineName.trim();
    const descriptionChanged = pipeline.description !== pipelineDescription.trim();
    const tagChanged = originalSystemTagId !== selectedSystemTagId;

    return nameChanged || descriptionChanged || tagChanged;
  };

  const isFormValid = () => {
    return (
      pipelineName.trim() !== '' &&
      pipelineName.length <= 50 &&
      pipelineDescription.trim() !== '' &&
      selectedSystemTagId !== ''
    );
  };

  const handleSubmit = () => {
    onSubmit({
      pipelineName: pipelineName.trim(),
      pipelineDescription: pipelineDescription.trim(),
      user_id,
      system_tag_id: selectedSystemTagId as number,
    });
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>
        {isEditMode ? "Edit Pipeline" : "Create New Pipeline"}
      </DialogTitle>
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

        <FormControl 
          fullWidth 
          margin="normal" 
          required 
          error={!selectedSystemTagId}
        >
          <InputLabel>{"Category"}</InputLabel>
          <Select
            value={selectedSystemTagId}
            onChange={(e) => setSelectedSystemTagId(e.target.value as number)}
            label="Category"
          >
            {systemTags.map((tag) => (
              <MenuItem key={tag.tag_id} value={tag.tag_id}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box
                    sx={{
                      width: 20,
                      height: 20,
                      borderRadius: '50%',
                      backgroundColor: tag.color
                    }}
                  />
                  {tag.name}
                </Box>
              </MenuItem>
            ))}
          </Select>
          {!selectedSystemTagId && (
            <FormHelperText>
              {"Please select a category for your pipeline"}
            </FormHelperText>
          )}
        </FormControl>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>{"Cancel"}</Button>
        <Button
          variant="contained"
          onClick={handleSubmit}
          disabled={!isFormValid() || (isEditMode && !hasChanges())}
        >
          {isEditMode ? "Save Changes" : "Create"}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default NewPipelineModal;