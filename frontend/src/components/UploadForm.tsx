import React, { useState, useRef } from "react";
import {
  Paper,
  Button,
  Typography,
  Box,
  Alert,
  LinearProgress,
} from "@mui/material";
import axios from "axios";
import { CloudUpload } from "@mui/icons-material";
import type { UploadFormProps } from "../types/index";
import { getCurrentToken } from "../services/auth";

const UploadForm: React.FC<UploadFormProps> = ({
  user,
  pipeline,
  onUploadSuccess,
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<string>("");
  const [uploadError, setUploadError] = useState<string>("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleUpload = async () => {
    if (!selectedFile || !user) return;

    setUploading(true);
    setUploadMessage("");
    setUploadError("");

    try {
      const token = await getCurrentToken();

      if (!token) {
        throw new Error("Not authenticated");
      }

      const formData = new FormData();
      formData.append("file", selectedFile);
      formData.append("pipeline_id", pipeline.pipeline_id.toString());
      formData.append("token", token);

      const response = await axios.post(
        "http://localhost:8000/api/upload-simple",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setUploadMessage(
        `Success! ${response.data.file_name} uploaded to Firebase Storage and ${pipeline.pipeline_name}. Download URL: ${response.data.download_url}`
      );
      setSelectedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

      if (onUploadSuccess) {
        onUploadSuccess();
      }
    } catch (error: any) {
      setUploadError(
        error.response?.data?.detail || error.message || "Upload failed"
      );
    } finally {
      setUploading(false);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.type === "application/pdf") {
        setSelectedFile(file);
      } else {
        alert("Please upload a PDF file");
      }
    }
  };

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: "#f5f5f5",
        padding: 4,
      }}
    >
      <Paper
        elevation={3}
        sx={{
          p: 4,
          width: "100%",
          maxWidth: 500,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 2,
        }}
      >
        <input
          type="file"
          accept="application/pdf"
          ref={fileInputRef}
          onChange={handleFileSelect}
          style={{ display: "none" }}
        />

        <Button
          variant="contained"
          component="span"
          startIcon={<CloudUpload />}
          onClick={handleUploadClick}
          sx={{ width: "100%" }}
        >
          Select PDF File
        </Button>

        {selectedFile && (
          <Box sx={{ width: "100%", mt: 2 }}>
            <Typography variant="body2" sx={{ mb: 1 }}>
              Selected: {selectedFile.name}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Size: {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
            </Typography>
            {uploadError && (
              <Alert severity="error" sx={{ mt: 2, mb: 2 }}>
                {uploadError}
              </Alert>
            )}
            {uploadMessage && (
              <Alert severity="success" sx={{ mt: 2, mb: 2 }}>
                {uploadMessage}
              </Alert>
            )}
            <Button
              variant="contained"
              fullWidth
              onClick={handleUpload}
              disabled={uploading}
              sx={{ mt: 2 }}
            >
              {uploading ? "Uploading..." : "Upload"}
            </Button>
            {uploading && <LinearProgress sx={{ mt: 2 }} />}
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default UploadForm;
