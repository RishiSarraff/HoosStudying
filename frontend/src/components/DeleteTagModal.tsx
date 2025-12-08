import type { DeleteTagModalProps } from "../types/index";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  Checkbox,
  Chip,
} from "@mui/material";
import { useState } from "react";
import DeleteIcon from "@mui/icons-material/Delete";

const DeleteTagModal: React.FC<DeleteTagModalProps> = ({
  open,
  onClose,
  onSubmit,
  listOfCustomTags,
}) => {
  const [selectedTagIds, setSelectedTagIds] = useState<number[]>([]);

  const handleToggle = (tagId: number) => {
    setSelectedTagIds((prev) => {
      if (prev.includes(tagId)) {
        return prev.filter((id) => id !== tagId);
      } else {
        return [...prev, tagId];
      }
    });
  };

  const handleSubmit = () => {
    selectedTagIds.forEach((tagId) => {
      onSubmit({ tag_id: tagId });
    });
    setSelectedTagIds([]);
  };

  const handleClose = () => {
    setSelectedTagIds([]);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} fullWidth maxWidth="sm">
      <DialogTitle>{"Delete Custom Tags"}</DialogTitle>
      <DialogContent>
        {listOfCustomTags && listOfCustomTags.length > 0 ? (
          <>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              {"Select the tags you want to delete from this pipeline"}
            </Typography>
            <List sx={{ maxHeight: 400, overflow: "auto" }}>
              {listOfCustomTags.map((tag) => (
                <ListItem key={tag.tag_id} disablePadding>
                  <ListItemButton
                    onClick={() => handleToggle(tag.tag_id)}
                    sx={{
                      borderRadius: 1,
                      mb: 0.5,
                      "&:hover": {
                        backgroundColor: "#F5F5F5",
                      },
                    }}
                  >
                    <ListItemIcon>
                      <Checkbox
                        edge="start"
                        checked={selectedTagIds.includes(tag.tag_id)}
                        tabIndex={-1}
                        disableRipple
                      />
                    </ListItemIcon>
                    <Chip
                      label={tag.name}
                      sx={{
                        backgroundColor: `${tag.color}20`,
                        color: tag.color,
                        fontWeight: 500,
                        "& .MuiChip-label": {
                          display: "flex",
                          alignItems: "center",
                          gap: 1,
                        },
                      }}
                      icon={
                        <Box
                          sx={{
                            width: 8,
                            height: 8,
                            borderRadius: "50%",
                            backgroundColor: tag.color,
                            ml: 1,
                          }}
                        />
                      }
                    />
                  </ListItemButton>
                </ListItem>
              ))}
            </List>

            {selectedTagIds.length > 0 && (
              <Box
                sx={{
                  mt: 2,
                  p: 2,
                  backgroundColor: "#FFF3E0",
                  borderRadius: 1,
                  border: "1px solid #FFB74D",
                }}
              >
                <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                  <DeleteIcon sx={{ color: "#F57C00", fontSize: 20 }} />
                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                    {selectedTagIds.length === 1
                      ? "1 tag will be deleted"
                      : `${selectedTagIds.length} tags will be deleted`}
                  </Typography>
                </Box>
                <Typography variant="caption" color="text.secondary">
                  {"This action cannot be undone"}
                </Typography>
              </Box>
            )}
          </>
        ) : (
          <Box
            sx={{
              py: 4,
              textAlign: "center",
              color: "text.secondary",
            }}
          >
            <Typography variant="body1">
              {"No custom tags found for this pipeline"}
            </Typography>
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>{"Cancel"}</Button>
        <Button
          variant="contained"
          color="error"
          onClick={handleSubmit}
          disabled={selectedTagIds.length === 0}
          startIcon={<DeleteIcon />}
        >
          {selectedTagIds.length === 0
            ? "Delete"
            : selectedTagIds.length === 1
            ? "Delete 1 Tag"
            : `Delete ${selectedTagIds.length} Tags`}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DeleteTagModal;