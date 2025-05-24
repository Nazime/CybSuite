import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
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
} from '@mui/material'
import TableSidebar from './TableSidebar'
import { API_ENDPOINTS } from '../config/api'

const DataDetail = () => {
  const { tableName, id } = useParams()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

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
          <Typography variant="h6" component="h2" sx={{ mb: 3 }}>
            {tableName.charAt(0).toUpperCase() + tableName.slice(1)} Details
          </Typography>

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
    </Box>
  )
}

export default DataDetail