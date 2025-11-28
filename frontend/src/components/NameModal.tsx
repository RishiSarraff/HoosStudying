import { useState } from "react";
import { Modal, Box, TextField, Button, Typography } from "@mui/material";
import type { NameModalProps } from "../types/index";

const style = {
  position: "absolute",
  top: "50%",
  left: "50%",
  transform: "translate(-50%, -50%)",
  width: 400,
  bgcolor: "background.paper",
  p: 4,
  borderRadius: 2,
};

export default function NameModal({ onSubmit }: NameModalProps) {
  const [first_name, setFirstName] = useState<string>("");
  const [last_name, setLastName] = useState<string>("");

  const handleSubmit = () => {
    if (first_name.trim() === "") return;
    onSubmit(first_name, last_name);
  };

  return (
    <Modal open={true}>
      <Box sx={style}>
        <Typography variant="h6" mb={2}>
          Welcome! Please enter your name
        </Typography>
        <TextField
          label="First Name"
          fullWidth
          sx={{ mb: 2 }}
          value={first_name}
          onChange={(e) => setFirstName(e.target.value)}
        />
        <TextField
          label="Last Name"
          fullWidth
          sx={{ mb: 3 }}
          value={last_name}
          onChange={(e) => setLastName(e.target.value)}
        />
        <Button variant="contained" fullWidth onClick={handleSubmit}>
          Continue
        </Button>
      </Box>
    </Modal>
  );
}
