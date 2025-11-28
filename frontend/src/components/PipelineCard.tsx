import type { PipelineCardProps } from "../types/index";
import { useTheme } from "@mui/material/styles";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import IconButton from "@mui/material/IconButton";
import DeleteIcon from "@mui/icons-material/Delete";
import Typography from "@mui/material/Typography";
import FolderIcon from "@mui/icons-material/Folder";

const PipelineCard: React.FC<PipelineCardProps> = ({
  pipeline_id,
  pipeline_name,
  pipeline_description,
  number_of_documents,
  index,
  onDelete,
}) => {
  return (
    <Card
      sx={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        p: 2,
        mb: 1.5,
        width: "100%",
        maxWidth: "100%",
        backgroundColor: "#ECECEC",
        cursor: "pointer",
        transition: "all 0.2s ease-in-out",
        border: "none",
        boxShadow: "none",
        boxSizing: "border-box",
        "&:hover": {
          backgroundColor: "#E0E0E0",
          boxShadow: "none",
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
            flexShrink: 0,
          }}
        >
          <FolderIcon sx={{ color: "#424242", fontSize: 28 }} />
          <Typography
            sx={{
              position: "absolute",
              fontSize: "0.7rem",
              fontWeight: 600,
              color: "#FFFFFF",
            }}
          >
            {index + 1}
          </Typography>
        </Box>

        <Box sx={{ flex: 1, minWidth: 0, overflow: "hidden" }}>
          <Typography
            variant="body1"
            component="div"
            sx={{
              fontWeight: 500,
              mb: 0.25,
              fontSize: "0.95rem",
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
              color: "#212121",
            }}
          >
            {pipeline_name}
          </Typography>

          <Typography
            variant="body2"
            sx={{
              color: "#757575",
              mb: 0.25,
              fontSize: "0.8rem",
            }}
          >
            {number_of_documents} {number_of_documents === 1 ? "file" : "files"}
          </Typography>

          <Typography
            variant="body2"
            sx={{
              color: "#BDBDBD",
              fontStyle: pipeline_description ? "normal" : "italic",
              fontSize: "0.8rem",
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
          >
            {pipeline_description || "No description"}
          </Typography>
        </Box>
      </Box>

      <IconButton
        aria-label="delete pipeline"
        onClick={(e) => {
          e.stopPropagation();
          if (onDelete) {
            onDelete();
          }
        }}
        sx={{
          backgroundColor: "transparent",
          color: "#424242",
          flexShrink: 0,
          ml: 1,
          p: 0.5,
          "&:hover": {
            backgroundColor: "transparent",
            color: "#212121",
          },
          transition: "all 0.2s ease-in-out",
        }}
      >
        <DeleteIcon sx={{ fontSize: 24 }} />
      </IconButton>
    </Card>
  );
};

export default PipelineCard;
