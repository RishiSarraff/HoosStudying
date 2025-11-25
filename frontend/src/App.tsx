import React, { useEffect, useState, useRef } from "react";
import { Typography, Button, Box, Paper, LinearProgress, Alert } from "@mui/material";
import { CloudUpload } from "@mui/icons-material";
import { onAuthStateChanged, signOut } from "firebase/auth";
import { auth } from "./firebase";
import AuthPage from "./AuthPage";
import axios from "axios";

const App: React.FC = () => {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<string>("");
  const [uploadError, setUploadError] = useState<string>("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUser(user);
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const handleLogout = async () => {
    try {
      await signOut(auth);
    } catch (error) {
      console.error("Error signing out", error);
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

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleUpload = async () => {
    if (!selectedFile || !user) return;
    
    setUploading(true);
    setUploadMessage("");
    setUploadError("");
    
    try {
      const token = await user.getIdToken();
      
      const formData = new FormData();
      formData.append("file", selectedFile);
      formData.append("token", token);
      
      const response = await axios.post("http://localhost:8000/api/upload-simple", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      
      setUploadMessage(`Success! Document uploaded to Firebase Storage. Download URL: ${response.data.download_url}`);
      setSelectedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (error: any) {
      setUploadError(error.response?.data?.detail || error.message || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  if (loading) {
    return (
      <Box
        sx={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <Typography variant="h4">Loading...</Typography>
      </Box>
    );
  }

  if (!user) {
    return <AuthPage />;
  }

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: "#f5f5f5",
        padding: 4,
      }}
    >
      <Typography variant="h1" sx={{ mb: 4, fontWeight: 600 }}>
        HoosStudying
      </Typography>
      
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
            {uploading && (
              <LinearProgress sx={{ mt: 2 }} />
            )}
          </Box>
        )}
      </Paper>

      <Button variant="outlined" onClick={handleLogout} sx={{ mt: 4 }}>
        Logout
      </Button>
    </Box>
  );
};

export default App;
