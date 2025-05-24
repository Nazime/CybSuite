import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import {
  Box,
  TextField,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  InputAdornment,
  IconButton,
  CircularProgress,
} from '@mui/material'
import {
  Search as SearchIcon,
  TableChart as TableChartIcon,
} from '@mui/icons-material'
import { API_ENDPOINTS } from '../config/api'

/**
 * DataView Component
 * Main entry point for data visualization. Shows a list of all available tables
 * that can be accessed in the system. Provides search functionality and
 * navigation to detailed table views.
 */
const DataView = () => {
  // Navigation hook for routing
  const navigate = useNavigate()

  // Component state management
  // List of available tables
  const [tables, setTables] = useState([])

  // Loading state indicator
  const [loading, setLoading] = useState(true)

  // Error state storage
  const [error, setError] = useState(null)

  // Search input value
  const [searchQuery, setSearchQuery] = useState('')

  // Fetch available tables on component mount
  useEffect(() => {
    const fetchTables = async () => {
      try {
        setLoading(true)
        const response = await axios.get(API_ENDPOINTS.SCHEMA.REQUEST)
        setTables(response.data)
        setError(null)
      } catch (err) {
        setError('Failed to fetch tables: ' + err.message)
        console.error('API Request failed:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchTables()
  }, [])

  // Filter tables based on search query
  const filteredTables = tables.filter(table =>
    table.toLowerCase().includes(searchQuery.toLowerCase())
  )

  // Loading state view
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
    )
  }

  // Error state view
  if (error) {
    return (
      <Box sx={{
        p: 2,
        minHeight: 'calc(100vh - 64px)',
        color: 'error.main'
      }}>
        <Typography>{error}</Typography>
      </Box>
    )
  }

  // Main component view
  return (
    <Box sx={{
      p: 2,
      minHeight: 'calc(100vh - 64px)',
      bgcolor: 'background.default'
    }}>
      <Paper sx={{
        overflow: 'hidden',
        p: { xs: 1, sm: 2 },
      }}>
        {/* Header section with title and search */}
        <Box sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 2,
          mb: 2
        }}>
          <Typography variant="h5" component="h2">
            Available Tables
          </Typography>

          <TextField
            size="small"
            placeholder="Search tables..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon color="action" />
                </InputAdornment>
              ),
            }}
            sx={{ width: { xs: '100%', sm: 250 } }}
          />
        </Box>

        {/* Table list */}
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Table Name</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>

            <TableBody>
              {filteredTables.map((table) => (
                <TableRow
                  key={table}
                  hover
                  sx={{ cursor: 'pointer' }}
                  onClick={() => navigate(`/data/request/${table}`)}
                >
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <TableChartIcon color="action" fontSize="small" />
                      {table}
                    </Box>
                  </TableCell>

                  <TableCell align="right">
                    <IconButton
                      color="primary"
                      onClick={(e) => {
                        e.stopPropagation()
                        navigate(`/data/request/${table}`)
                      }}
                    >
                      <TableChartIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  )
}

export default DataView