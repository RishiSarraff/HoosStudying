import { Button } from "@mui/material";
import FolderIcon from "@mui/icons-material/Folder";
import type { FileButtonProps } from "../types";

const FilesButton: React.FC<FileButtonProps> = ({
  onClick,
  isActive = false,
}) => {
  return (
    <Button
      variant={isActive ? "contained" : "outlined"}
      startIcon={<FolderIcon />}
      onClick={onClick}
      sx={{
        textTransform: "none",
        backgroundColor: isActive ? "#1976D2" : "transparent",
        color: isActive ? "#FFFFFF" : "#212121",
        borderColor: "#212121",
        "&:hover": {
          backgroundColor: isActive ? "#1565C0" : "rgba(0, 0, 0, 0.04)",
        },
      }}
    >
      Files
    </Button>
  );
};

export default FilesButton;
