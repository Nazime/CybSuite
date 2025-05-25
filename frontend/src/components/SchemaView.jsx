import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import {
  Box,
  List,
  ListItem,
  ListItemText,
  TextField,
  InputAdornment,
  Typography,
  Paper,
  CircularProgress,
} from '@mui/material'
import {
  Search as SearchIcon,
} from '@mui/icons-material'
import { API_ENDPOINTS } from '../config/api'

const SchemaView = () => {
  const navigate = useNavigate()
  const [tables, setTables] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')

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

  const filteredTables = tables.filter(table =>
    table.toLowerCase().includes(searchQuery.toLowerCase())
  )

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

  if (error) {
    return (
      <Box sx={{
        p: 3,
        color: 'error.main',
        minHeight: 'calc(100vh - 64px)',
      }}>
        <Typography>{error}</Typography>
      </Box>
    )
  }

  return (
    <Box sx={{ p: 2 }}>
      <Paper sx={{
        overflow: 'hidden',
        maxWidth: 800,
        mx: 'auto',
      }}>
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="h6" component="h2" gutterBottom>
            Available Schemas
          </Typography>
          <TextField
            size="small"
            fullWidth
            placeholder="Search schemas..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon fontSize="small" />
                </InputAdornment>
              ),
            }}
          />
        </Box>

        <List
          dense
          disablePadding
          sx={{
            py: 0.5,
            '& .MuiListItem-root': {
              minHeight: 32,
              borderRadius: 1,
              mx: 1,
              my: '2px',
              px: 1.5,
              '& .MuiListItemText-root': {
                margin: 0,
              },
              '& .MuiTypography-root': {
                fontSize: '0.875rem',
                lineHeight: 1.2,
              },
            },
            '& .MuiListItem-root:hover': {
              bgcolor: 'action.hover',
            },
          }}
        >
          {filteredTables.map((table) => (
            <ListItem
              key={table}
              button
              onClick={() => navigate(`/schema/${table}`)}
            >
              <ListItemText
                primary={table}
              />
            </ListItem>
          ))}
        </List>
      </Paper>
    </Box>
  )
}

export default SchemaView
