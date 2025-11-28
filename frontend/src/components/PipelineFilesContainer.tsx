import { useState, useEffect } from "react";
import {
  type PipelineDocument,
  type PipelineFilesContainerProps,
} from "../types/index";
import { getCurrentToken } from "../services/auth";
import { getPipelineDocuments } from "../services/document";
import {
  Box,
  Card,
  CardContent,
  CircularProgress,
  Grid,
  Typography,
} from "@mui/material";
import PictureAsPdfIcon from "@mui/icons-material/PictureAsPdf";

const PipelineFilesContainer: React.FC<PipelineFilesContainerProps> = ({
  user,
  pipeline,
}) => {
  // We want to get the specific documents from each user and pipeline
  const [files, setFiles] = useState<PipelineDocument[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchDocuments = async () => {
    setLoading(true);

    const token = await getCurrentToken();
    if (token) {
      const documents = await getPipelineDocuments(token, pipeline.pipeline_id);
      setFiles(documents);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchDocuments();
  }, [pipeline.pipeline_id]);

  if (loading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          minHeight: "100vh",
          backgroundColor: "#CACACA",
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box
      sx={{
        minHeight: "100vh",
        backgroundColor: "#CACACA",
        padding: 4,
      }}
    >
      <Typography
        variant="h4"
        sx={{ mb: 4, fontWeight: 700, color: "#212121" }}
      >
        Files in {pipeline.pipeline_name}
      </Typography>

      <Typography variant="h6" sx={{ mb: 2, color: "#424242" }}>
        {files.length} {files.length === 1 ? "file" : "files"}
      </Typography>

      {files.length === 0 ? (
        <Box sx={{ textAlign: "center", mt: 8 }}>
          <Typography variant="h6" sx={{ color: "#757575" }}>
            No files uploaded yet
          </Typography>
          <Typography variant="body2" sx={{ color: "#BDBDBD", mt: 1 }}>
            Upload files using the "Upload Files" button above
          </Typography>
        </Box>
      ) : (
        <Grid container spacing={3} sx={{ mt: 2 }}>
          {files.map((file) => (
            <Grid size={8} key={file.document_id}>
              <Card
                sx={{
                  backgroundColor: "#FFFFFF",
                  "&:hover": {
                    boxShadow: 3,
                    transform: "translateY(-2px)",
                    transition: "all 0.2s",
                    cursor: "pointer",
                  },
                }}
              >
                <CardContent>
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      gap: 1,
                      mb: 1,
                    }}
                  >
                    <PictureAsPdfIcon color="error" />
                    <Typography variant="h6" noWrap>
                      {file.file_name}
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    Type: {file.file_type}
                  </Typography>
                  <Typography
                    variant="caption"
                    color="text.secondary"
                    sx={{ display: "block", mt: 1 }}
                  >
                    Uploaded: {new Date(file.upload_date).toLocaleDateString()}
                  </Typography>
                  <Typography
                    variant="caption"
                    sx={{
                      display: "block",
                      mt: 0.5,
                      color: file.is_active ? "success.main" : "text.disabled",
                    }}
                  >
                    Status: {file.is_active ? "Active" : "Inactive"}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
};

export default PipelineFilesContainer;
