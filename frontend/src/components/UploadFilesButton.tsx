import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from "@mui/material";
import { type UploadFormProps } from "../types/index";
import UploadForm from "./UploadForm";
import { useState } from "react";

const UploadFilesButton: React.FC<UploadFormProps> = ({
  user,
  pipeline,
  onUploadSuccess,
}) => {
  const [openUploadFormModal, setOpenUploadFormModal] =
    useState<boolean>(false);

    const handleUploadSuccess = () => {
        if (onUploadSuccess){
            onUploadSuccess();
        }
        setOpenUploadFormModal(false)
    }

  return (
    <>
      <Button onClick={() => setOpenUploadFormModal(true)}>Upload Files</Button>

      <Dialog
        open={openUploadFormModal}
        onClose={() => setOpenUploadFormModal(false)}
        fullWidth
        maxWidth="sm"
      >
        <DialogTitle>Upload a File to Pipeline</DialogTitle>
        <DialogContent
          sx={{
            overflow: "visible",
            pt: 2,
            pb: 3,
          }}
        >
          <UploadForm
            user={user}
            pipeline={pipeline}
            onUploadSuccess={handleUploadSuccess}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenUploadFormModal(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default UploadFilesButton;
