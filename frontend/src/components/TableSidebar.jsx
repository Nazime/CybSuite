import React, { useState, useEffect } from 'react'
import { useNavigate, useParams, useLocation } from 'react-router-dom'
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
  IconButton,
} from '@mui/material'
import {
  Search as SearchIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
} from '@mui/icons-material'
import { useSidebar } from '../contexts/SidebarContext'
import { API_ENDPOINTS } from '../config/api'

const TableSidebar = () => {
  const navigate = useNavigate()
  const { tableName: currentTable } = useParams()
  const location = useLocation()
  const [searchQuery, setSearchQuery] = useState('')
  const [tables, setTables] = useState([])
  const [error, setError] = useState(null)
  const { isCollapsed, toggleSidebar } = useSidebar()

  // Determine if we're in schema or request context
  const isSchemaContext = location.pathname.startsWith('/schema')
  const baseUrl = isSchemaContext ? '/schema' : '/data/request'

  useEffect(() => {
    const fetchTables = async () => {
      try {
        const response = await axios.get(API_ENDPOINTS.SCHEMA.REQUEST)
        setTables(response.data)
        setError(null)
      } catch (err) {
        setError('Failed to fetch tables: ' + err.message)
        console.error('API Request failed:', err)
      }
    }

    fetchTables()
  }, [])

  const filteredTables = tables.filter(table =>
    table.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <Box
      sx={{
        width: isCollapsed ? 48 : 240,
        flexShrink: 0,
        transition: 'width 0.2s ease',
        height: '100%',
        overflow: 'hidden',
      }}
    >
      <Paper
        elevation={0}
        sx={{
          height: '100%',
          width: 240,
          borderRight: '1px solid',
          borderColor: 'divider',
          bgcolor: 'background.default',
          display: 'flex',
          flexDirection: 'column',
          transform: isCollapsed ? 'translateX(-192px)' : 'none',
          transition: 'transform 0.2s ease',
        }}
      >
        <Box sx={{
          p: 1.5,
          borderBottom: 1,
          borderColor: 'divider',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          minHeight: '48px',
        }}>
          {!isCollapsed && (
            <Box sx={{ flex: 1 }}>
              <Typography variant="subtitle2" sx={{ mb: 1, pl: 1 }}>
                Tables
              </Typography>
              <TextField
                size="small"
                fullWidth
                placeholder="Search tables..."
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
          )}
          <IconButton
            onClick={toggleSidebar}
            size="small"
            sx={{
              ml: isCollapsed ? 0 : 1,
              transform: isCollapsed ? 'translateX(192px)' : 'none',
              transition: 'transform 0.2s ease',
            }}
          >
            {isCollapsed ? <ChevronRightIcon /> : <ChevronLeftIcon />}
          </IconButton>
        </Box>

        {!isCollapsed && (
          <List
            dense
            disablePadding
            sx={{
              flexGrow: 1,
              overflow: 'auto',
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
              '& .MuiListItem-root.Mui-selected': {
                bgcolor: 'primary.main',
                color: 'primary.contrastText',
                '&:hover': {
                  bgcolor: 'primary.dark',
                },
              },
            }}
          >
            {filteredTables.map((table) => (
              <ListItem
                key={table}
                button
                selected={table === currentTable}
                onClick={() => navigate(`${baseUrl}/${table}`)}
              >
                <ListItemText
                  primary={table}
                />
              </ListItem>
            ))}
          </List>
        )}
      </Paper>
    </Box>
  )
}

export default TableSidebar
