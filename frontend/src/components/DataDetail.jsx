import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'
import {
  Box,
  Paper,
  Typography,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Alert,
  Snackbar,
} from '@mui/material'
import { Delete as DeleteIcon } from '@mui/icons-material'
import TableSidebar from './TableSidebar'
import { API_ENDPOINTS } from '../config/api'

const DataDetail = () => {
  const { tableName, id } = useParams()
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [deleteError, setDeleteError] = useState(null)

  useEffect(() => {
    const fetchDetail = async () => {
      try {
        setLoading(true)
        const response = await axios.get(API_ENDPOINTS.DATA.DETAIL(tableName, id))
        setData(response.data)
        setError(null)
      } catch (err) {
        setError('Failed to fetch detail: ' + err.message)
        console.error('API Request failed:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchDetail()
  }, [tableName, id])

  const handleDelete = async () => {
    try {
      await axios.delete(API_ENDPOINTS.DATA.DELETE(tableName, id))
      setDeleteDialogOpen(false)
      // Navigate back to list after deletion
      navigate(`/data/request/${tableName}`)
    } catch (err) {
      setDeleteError('Failed to delete: ' + err.message)
      console.error('Delete failed:', err)
    }
  }

  if (loading) {
    return (
      <Box sx={{
        height: 'calc(100vh - 64px)',
        display: 'flex',
      }}>
        <TableSidebar />
        <Box sx={{
          flex: 1,
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
        }}>
          <CircularProgress />
        </Box>
      </Box>
    )
  }

  if (error) {
    return (
      <Box sx={{
        height: 'calc(100vh - 64px)',
        display: 'flex',
      }}>
        <TableSidebar />
        <Box sx={{
          flex: 1,
          p: 2,
          color: 'error.main',
        }}>
          <Typography>{error}</Typography>
        </Box>
      </Box>
    )
  }

  return (
    <Box sx={{
      height: 'calc(100vh - 64px)',
      display: 'flex',
    }}>
      <TableSidebar />
      <Box sx={{
        flex: 1,
        p: 2,
        overflow: 'auto',
      }}>
        <Paper sx={{
          overflow: 'hidden',
          p: { xs: 1, sm: 2 },
        }}>
          <Box sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            mb: 3,
          }}>
            <Typography variant="h6" component="h2">
              {tableName.charAt(0).toUpperCase() + tableName.slice(1)} Details
            </Typography>
            <Button
              variant="contained"
              color="error"
              startIcon={<DeleteIcon />}
              onClick={() => setDeleteDialogOpen(true)}
            >
              Delete
            </Button>
          </Box>

          <TableContainer>
            <Table
              size="small"
              sx={{
                '& .MuiTableCell-root': {
                  py: 1,
                  px: 2,
                  fontSize: '0.875rem',
                  lineHeight: 1.2,
                },
                '& .MuiTableCell-head': {
                  fontWeight: 600,
                  bgcolor: 'background.default',
                  width: '200px',
                },
              }}
            >
              <TableBody>
                {data && Object.entries(data).map(([key, value]) => (
                  <TableRow key={key}>
                    <TableCell component="th" scope="row" sx={{ fontWeight: 500 }}>
                      {key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                    </TableCell>
                    <TableCell>
                      {value === null ? '-' : String(value)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      </Box>

      {/* Delete confirmation dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>Confirm Deletion</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete this {tableName}? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleDelete} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Error notification snackbar */}
      <Snackbar
        open={!!deleteError}
        autoHideDuration={6000}
        onClose={() => setDeleteError(null)}
      >
        <Alert onClose={() => setDeleteError(null)} severity="error">
          {deleteError}
        </Alert>
      </Snackbar>
    </Box>
  )
}

export default DataDetail
