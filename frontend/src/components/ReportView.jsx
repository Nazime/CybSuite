import React, { useState, useEffect } from 'react';
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
} from '@mui/material';
import {
  Download as DownloadIcon,
} from '@mui/icons-material';
import { API_ENDPOINTS } from '../config/api';

const ReportView = () => {
  const [reporters, setReporters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });

  useEffect(() => {
    const fetchReporters = async () => {
      try {
        setLoading(true);
        const response = await axios.get(API_ENDPOINTS.PLUGINS.REPORTERS);
        setReporters(response.data);
        setError(null);
      } catch (err) {
        setError('Failed to fetch reporters: ' + err.message);
        console.error('API Request failed:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchReporters();
  }, []);

  const handleGenerateReport = async (reporterName) => {
    try {
      // Use blob to handle file download
      const response = await axios.get(API_ENDPOINTS.REPORT.GENERATE(reporterName), {
        responseType: 'blob'
      });

      // Get filename from Content-Disposition header
      const contentDisposition = response.headers['content-disposition'];
      const filename = contentDisposition
        ? contentDisposition.split('filename=')[1].replace(/["']/g, '')
        : `report_${reporterName}`;

      // Create a URL for the blob
      const url = window.URL.createObjectURL(new Blob([response.data]));

      // Create a temporary link element and trigger download
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();

      // Clean up the URL
      window.URL.revokeObjectURL(url);

      setSnackbar({
        open: true,
        message: 'Report generated successfully!',
        severity: 'success'
      });
    } catch (err) {
      console.error('Failed to generate report:', err);
      setSnackbar({
        open: true,
        message: 'Failed to generate report: ' + err.message,
        severity: 'error'
      });
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
        Available Reports
      </Typography>

      <Paper elevation={2}>
        <List>
          {reporters.map((reporter) => (
            <ListItem key={reporter.name} divider>
              <ListItemText
                primary={reporter.name}
              />
              <ListItemSecondaryAction>
                <IconButton
                  edge="end"
                  aria-label="generate report"
                  onClick={() => handleGenerateReport(reporter.name)}
                >
                  <DownloadIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      </Paper>

      {reporters.length === 0 && (
        <Typography sx={{ mt: 2, textAlign: 'center', color: 'text.secondary' }}>
          No reporters available
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

export default ReportView;
