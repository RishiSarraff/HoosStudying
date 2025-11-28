import * as React from "react";
import Snackbar, { type SnackbarCloseReason } from "@mui/material/Snackbar";
import { type AlertProps } from "../types/index";
import { Alert } from "@mui/material";

const CustomAlert: React.FC<AlertProps> = ({
  message,
  open,
  onClose,
  severity = "success",
}) => {
  const handleClose = (
    event: React.SyntheticEvent | Event,
    reason?: SnackbarCloseReason
  ) => {
    if (reason === "clickaway") {
      return;
    }

    onClose();
  };

  return (
    <Snackbar
      open={open}
      autoHideDuration={3000}
      onClose={handleClose}
      anchorOrigin={{ vertical: "top", horizontal: "center" }}
    >
      <Alert onClose={handleClose} severity={severity} sx={{ width: "100%" }}>
        {message}
      </Alert>
    </Snackbar>
  );
};

export default CustomAlert;
