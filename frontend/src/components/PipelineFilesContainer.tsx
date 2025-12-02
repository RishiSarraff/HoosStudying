import { useState, useEffect } from "react";
import {
  type PipelineDocument,
  type PipelineFilesContainerProps,
} from "../types/index";
import { getCurrentToken } from "../services/auth";
import { getDocumentMetadata, getFirebaseDownloadUrl, getPipelineDocuments, deleteDocumentFromPipeline} from "../services/document";
import {
  Box,
  Card,
  CardContent,
  CircularProgress,
  Grid,
  IconButton,
  Typography,
} from "@mui/material";
import PictureAsPdfIcon from "@mui/icons-material/PictureAsPdf";
import VisibilityIcon from '@mui/icons-material/Visibility';
import DownloadIcon from '@mui/icons-material/Download';
import DeleteIcon from '@mui/icons-material/Delete';
import CustomAlert from "./CustomAlert";


const PipelineFilesContainer: React.FC<PipelineFilesContainerProps> = ({
  user,
  pipeline,
  onDocumentChange
}) => {
  // We want to get the specific documents from each user and pipeline
  const [files, setFiles] = useState<PipelineDocument[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [alertState, setAlertState] = useState({
      open: false,
      message: "",
      severity: "success" as "success" | "error",
    });

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

  const displayDocumentHandler = async(file: PipelineDocument) => {
    const token = await getCurrentToken();

    if(token){
      const metadata = await getDocumentMetadata(token, file.document_id)

      const downloadUrl = await getFirebaseDownloadUrl(metadata.firebase_storage_path);

      window.open(downloadUrl, '_blank');
    }
  }

  const downloadDocumentHandler = async(file: PipelineDocument) => {
    const token = await getCurrentToken();

    if(token){
      try{
      const metadata = await getDocumentMetadata(token, file.document_id)

      const downloadUrl = await getFirebaseDownloadUrl(metadata.firebase_storage_path);

      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = file.file_name;
      link.setAttribute('target', '_blank');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      }
      catch (error) {
        console.error("Error downloading document:", error);
        setAlertState({
          open: true,
          message: "Failed to download document",
          severity: "error"
        });
      }
    }
  }

  const deleteDocumentFromPipelineHandler = async(pipeline_id: number, document_id: number) => {
    const token = await getCurrentToken();
    if (token) {
      try{
        const deleteDocumentFromPipelineResponse = await deleteDocumentFromPipeline(
          token,
          pipeline_id,
          document_id
        );
        if (deleteDocumentFromPipelineResponse) {
          setFiles(prevFiles => 
            prevFiles.filter(f => f.document_id !== document_id)
          );
          setAlertState({
            open: true,
            message: "Successfully Deleted Document from Pipeline",
            severity: "success"
          });
          if (onDocumentChange) {
            onDocumentChange();
          }
        } else {
          setAlertState({
            open: true,
            message: "Failed to Delete Document from Pipeline",
            severity: "error"
          });
        }
      }catch (error) {
        console.error("Error deleting document:", error);
        setAlertState({
          open: true,
          message: "Error Deleting Document from Pipeline",
          severity: "error"
        });
      }
    }
  }

  return (
    <Box
      sx={{
        minHeight: "100vh",
        backgroundColor: "#E0F3FF",
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
            <Grid size={12} key={file.document_id}>
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
                      flexDirection:"row",
                      justifyContent: "space-between",
                      alignItems: "center",
                      gap: 2  ,
                    }}
                  >
                    <Box
                      sx={{
                        display: "flex",
                        flexDirection:"column",
                        gap: 1,
                      }}
                    >
                      <Box
                        sx={{
                          display: "flex",
                          flexDirection:"row",
                          gap: 1,
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
                    </Box>
                    <Box
                      sx={{
                        display: "flex",
                        flexDirection:"row",
                        alignItems: "center",
                        gap: 1,
                      }}
                    >
                      <IconButton onClick={() => displayDocumentHandler(file)}>
                        <VisibilityIcon />
                      </IconButton>
                      <IconButton onClick={() => downloadDocumentHandler(file)}>
                        <DownloadIcon />
                      </IconButton>
                      <IconButton onClick={() => deleteDocumentFromPipelineHandler(pipeline.pipeline_id, file.document_id)}>
                        <DeleteIcon />
                      </IconButton>

                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
      <CustomAlert
        message={alertState.message}
        open={alertState.open}
        severity={alertState.severity}
        onClose={() => setAlertState((prev) => ({ ...prev, open: false }))}
      />
    </Box>
  );
};

export default PipelineFilesContainer;
