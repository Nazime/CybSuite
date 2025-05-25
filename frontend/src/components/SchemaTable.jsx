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
  Chip,
} from '@mui/material'
import {
  Check as CheckIcon,
} from '@mui/icons-material'
import TableSidebar from './TableSidebar'
import { API_ENDPOINTS } from '../config/api'

const SchemaTable = () => {
  const { tableName } = useParams()
  const [schema, setSchema] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchSchema = async () => {
      try {
        setLoading(true)
        const response = await axios.get(API_ENDPOINTS.SCHEMA.DETAIL(tableName))
        setSchema(response.data)
        setError(null)
      } catch (err) {
        setError('Failed to fetch schema: ' + err.message)
        console.error('API Request failed:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchSchema()
  }, [tableName])

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
            {tableName.charAt(0).toUpperCase() + tableName.slice(1)} Schema
          </Typography>

          <TableContainer>
            <Table
              size="small"
              sx={{
                '& .MuiTableCell-root': {
                  py: 0.75,
                  px: 1.5,
                  fontSize: '0.875rem',
                  lineHeight: 1.2,
                },
                '& .MuiTableCell-head': {
                  fontWeight: 600,
                  bgcolor: 'background.default',
                },
                '& .MuiTableRow-root:hover': {
                  bgcolor: 'action.hover',
                },
              }}
            >
              <TableHead>
                <TableRow>
                  <TableCell>Field Name</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell align="right">Properties</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {Object.entries(schema.fields).map(([fieldName, fieldInfo]) => (
                  <TableRow key={fieldName} hover>
                    <TableCell sx={{ fontWeight: 500 }}>
                      {fieldName}
                    </TableCell>
                    <TableCell>{fieldInfo.type}</TableCell>
                    <TableCell>{fieldInfo.description || '-'}</TableCell>
                    <TableCell align="right">
                      <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                        {fieldInfo.indexed && (
                          <Chip
                            size="small"
                            icon={<CheckIcon />}
                            label="Indexed"
                            color="primary"
                          />
                        )}
                        {fieldInfo.hidden_in_list && (
                          <Chip
                            size="small"
                            label="Hidden"
                            color="default"
                          />
                        )}
                      </Box>
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

export default SchemaTable
