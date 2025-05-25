import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import {
  Box,
  Paper,
  Typography,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Alert,
  Snackbar,
  Button,
  LinearProgress,
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  Delete as DeleteIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { API_ENDPOINTS } from '../config/api';

const IngestView = () => {
  const [ingestors, setIngestors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
  const [dragActive, setDragActive] = useState(false);
  const [files, setFiles] = useState([]);
  const [uploadProgress, setUploadProgress] = useState({});

  useEffect(() => {
    const fetchIngestors = async () => {
      try {
        setLoading(true);
        const response = await axios.get(API_ENDPOINTS.INGEST.PLUGINS);
        setIngestors(response.data);
        setError(null);
      } catch (err) {
        setError('Failed to fetch ingestors: ' + err.message);
        console.error('API Request failed:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchIngestors();
  }, []);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const droppedFiles = Array.from(e.dataTransfer.files);
    setFiles(prev => [...prev, ...droppedFiles.map(file => ({
      file,
      status: 'pending', // pending, uploading, success, error
      error: null
    }))]);
  }, []);

  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles(prev => [...prev, ...selectedFiles.map(file => ({
      file,
      status: 'pending',
      error: null
    }))]);
  };

  const handleRemoveFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleIngest = async (ingestorName) => {
    // Filter only pending files
    const pendingFiles = files.filter(f => f.status === 'pending');

    if (pendingFiles.length === 0) {
      setSnackbar({
        open: true,
        message: 'No files to upload',
        severity: 'warning'
      });
      return;
    }

    // Process each file
    for (let i = 0; i < pendingFiles.length; i++) {
      const fileIndex = files.findIndex(f => f === pendingFiles[i]);
      const fileData = pendingFiles[i];

      try {
        // Update status to uploading
        setFiles(prev => prev.map((f, idx) =>
          idx === fileIndex ? { ...f, status: 'uploading' } : f
        ));

        const formData = new FormData();
        formData.append('file', fileData.file);

        const response = await axios.post(
          API_ENDPOINTS.INGEST.UPLOAD(ingestorName),
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
            onUploadProgress: (progressEvent) => {
              const progress = (progressEvent.loaded / progressEvent.total) * 100;
              setUploadProgress(prev => ({
                ...prev,
                [fileIndex]: Math.round(progress)
              }));
            },
          }
        );

        // Update status to success
        setFiles(prev => prev.map((f, idx) =>
          idx === fileIndex ? { ...f, status: 'success' } : f
        ));

        setSnackbar({
          open: true,
          message: `Successfully ingested ${fileData.file.name}`,
          severity: 'success'
        });

      } catch (err) {
        console.error('Failed to ingest file:', err);

        // Update status to error
        setFiles(prev => prev.map((f, idx) =>
          idx === fileIndex ? {
            ...f,
            status: 'error',
            error: err.response?.data?.detail || err.message
          } : f
        ));

        setSnackbar({
          open: true,
          message: `Failed to ingest ${fileData.file.name}: ${err.message}`,
          severity: 'error'
        });
      }
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  if (loading) {
    return (
      <Box sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: 'calc(100vh - 64px)',
      }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{
        p: 3,
        color: 'error.main',
        minHeight: 'calc(100vh - 64px)',
      }}>
        <Typography>{error}</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, maxWidth: 800, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        Data Ingestion
      </Typography>

      {/* Drag & Drop Zone */}
      <Paper
        sx={{
          p: 3,
          mb: 3,
          border: '2px dashed',
          borderColor: dragActive ? 'primary.main' : 'grey.300',
          backgroundColor: dragActive ? 'action.hover' : 'background.paper',
          textAlign: 'center',
          cursor: 'pointer',
        }}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => document.getElementById('file-upload').click()}
      >
        <input
          type="file"
          id="file-upload"
          multiple
          style={{ display: 'none' }}
          onChange={handleFileSelect}
        />
        <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          Drag and drop files here
        </Typography>
        <Typography color="textSecondary">
          or click to select files
        </Typography>
      </Paper>

      {/* File List */}
      {files.length > 0 && (
        <Paper elevation={2} sx={{ mb: 3 }}>
          <List>
            {files.map((fileData, index) => (
              <ListItem key={index} divider>
                <ListItemText
                  primary={fileData.file.name}
                  secondary={
                    fileData.status === 'error' ? (
                      <Typography color="error">{fileData.error}</Typography>
                    ) : fileData.status === 'uploading' ? (
                      <LinearProgress
                        variant="determinate"
                        value={uploadProgress[index] || 0}
                      />
                    ) : null
                  }
                />
                <ListItemSecondaryAction>
                  {fileData.status === 'success' ? (
                    <CheckCircleIcon color="success" />
                  ) : fileData.status === 'error' ? (
                    <ErrorIcon color="error" />
                  ) : (
                    <IconButton
                      edge="end"
                      onClick={() => handleRemoveFile(index)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  )}
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        </Paper>
      )}

      {/* Ingestors List */}
      <Paper elevation={2}>
        <List>
          {ingestors.map((ingestor) => (
            <ListItem key={ingestor.name} divider>
              <ListItemText
                primary={ingestor.name}
              />
              <ListItemSecondaryAction>
                <Button
                  variant="contained"
                  onClick={() => handleIngest(ingestor.name)}
                  disabled={!files.some(f => f.status === 'pending')}
                >
                  Ingest Files
                </Button>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      </Paper>

      {ingestors.length === 0 && (
        <Typography sx={{ mt: 2, textAlign: 'center', color: 'text.secondary' }}>
          No ingestors available
        </Typography>
      )}

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default IngestView;
