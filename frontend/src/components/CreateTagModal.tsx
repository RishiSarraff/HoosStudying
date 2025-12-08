import type { CreateTagModalProps } from "../types/index";
import TextField from "@mui/material/TextField";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
} from "@mui/material";
import { useState} from "react"
import Circle from "@uiw/react-color-circle"

const CreateTagModal: React.FC<CreateTagModalProps> = ({
  user_id,
  open,
  onClose,
  onSubmit,
  pipeline_id
}) => {
  const [tagName, setTagName] = useState<string>('')
  const [tagColor, setTagColor] = useState<string>('#3B82F6')

  const colorPresets = [
    '#3B82F6', // Blue
    '#10B981', // Green
    '#F59E0B', // Amber
    '#EF4444', // Red
    '#8B5CF6', // Purple
    '#EC4899', // Pink
    '#14B8A6', // Teal
    '#F97316', // Orange
    '#6366F1', // Indigo
    '#84CC16', // Lime
    '#06B6D4', // Cyan
    '#A855F7', // Violet
  ];

  const isFormValid = () => {
    return tagName.trim() !== '' && tagName.length <= 50 && tagColor !== '';
  };

  const handleSubmit = () => {
    if (isFormValid()) {
      onSubmit({
        pipeline_id: pipeline_id,
        user_id: user_id,
        name: tagName.trim(),
        color: tagColor
      });
      setTagName('');
      setTagColor('#3B82F6');
    }
  };

  const handleClose = () => {
    setTagName('');
    setTagColor('#3B82F6');
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} fullWidth maxWidth="sm">
      <DialogTitle>
        {"Create Tags for the Pipeline"}
      </DialogTitle>
      <DialogContent>
        <TextField
          fullWidth
          required
          label="Tag Name"
          value={tagName}
          onChange={(e) => setTagName(e.target.value)}
          error={tagName.length > 50}
          helperText={
            tagName.length > 50 ? "Pipeline Name is too long" : ""
          }
          margin="normal"
        />
        <Box sx={{ mt: 3 }}>
          <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
            {"Choose a color"}
          </Typography>
            <Circle 
                colors={colorPresets}
                color={tagColor}
                onChange={(color: any) => {
                    setTagColor(color.hex);
                }}    
            />
        </Box>
        <Box sx={{ mt: 3, p: 2, backgroundColor: '#F5F5F5', borderRadius: 1 }}>
          <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
            {"Preview"}
          </Typography>
          {tagName ? (
            <Box sx={{ 
              display: 'inline-flex', 
              alignItems: 'center',
              backgroundColor: `${tagColor}20`,
              color: tagColor,
              padding: '4px 12px',
              borderRadius: '16px',
              fontSize: '0.875rem',
              fontWeight: 500,
              gap: '4px'
            }}>
              <Box sx={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                backgroundColor: tagColor
              }} />
              {tagName}
            </Box>
          ) : (
            <Typography variant="caption" color="text.secondary">
              {"Enter a tag name to see preview"}
            </Typography>
          )}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>{"Cancel"}</Button>
        <Button
          variant="contained"
          onClick={handleSubmit}
        >
          {"Create"}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CreateTagModal;