import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react'
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
  TablePagination,
  IconButton,
  Button,
  TextField,
  InputAdornment,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Alert,
  Snackbar,
  Menu,
  MenuItem,
  Checkbox,
  FormControlLabel,
  Tooltip,
  Popover,
} from '@mui/material'
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  ViewColumn as ViewColumnIcon,
  FilterAlt as FilterIcon,
  Clear as ClearIcon,
} from '@mui/icons-material'
import TableSidebar from './TableSidebar'
import { API_ENDPOINTS } from '../config/api'

/**
 * DataTable Component
 * Displays a detailed view of a specific table's data with features like:
 * - Pagination
 * - Search/filtering
 * - Row deletion
 * - Navigation to detailed views
 * - Sidebar navigation
 */
const DataTable = () => {
  // Route parameters and navigation
  const { tableName } = useParams()
  const navigate = useNavigate()

  // Data and UI state management
  // Table data
  const [data, setData] = useState([])

  // Loading state
  const [loading, setLoading] = useState(true)

  // Error state
  const [error, setError] = useState(null)

  // Current page number
  const [page, setPage] = useState(0)

  // Items per page
  const [rowsPerPage, setRowsPerPage] = useState(10)

  // Search/filter query
  const [searchQuery, setSearchQuery] = useState('')

  // Delete operation state management
  // Dialog visibility
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)

  // Delete operation error
  const [deleteError, setDeleteError] = useState(null)

  // Item selected for deletion
  const [selectedItem, setSelectedItem] = useState(null)

  // Reference for the search input
  const searchInputRef = useRef(null)

  // Column visibility state
  const [columnVisibility, setColumnVisibility] = useState({})
  const [columnMenuAnchor, setColumnMenuAnchor] = useState(null)
  const [columnsInitialized, setColumnsInitialized] = useState(false)
  const [tableSchema, setTableSchema] = useState(null)

  // Column filters state
  const [columnFilters, setColumnFilters] = useState({})
  const [filterAnchor, setFilterAnchor] = useState({})

  /**
   * Fetches table data from the API with pagination
   * Updates the data state and handles loading/error states
   */
  const fetchData = useCallback(async () => {
    try {
      setLoading(true)
      // Store the current selection range
      const selectionStart = searchInputRef.current?.selectionStart
      const selectionEnd = searchInputRef.current?.selectionEnd
      const hasFocus = document.activeElement === searchInputRef.current

      const response = await axios.get(`${API_ENDPOINTS.DATA.REQUEST(tableName)}`, {
        params: {
          skip: page * rowsPerPage,
          limit: rowsPerPage,
          search: searchQuery || undefined,
          filters: Object.keys(columnFilters).length > 0 ? JSON.stringify(columnFilters) : undefined
        }
      })
      setData(response.data)
      setError(null)

      // Restore focus and selection after state update
      if (hasFocus) {
        setTimeout(() => {
          searchInputRef.current?.focus()
          if (typeof selectionStart === 'number' && typeof selectionEnd === 'number') {
            searchInputRef.current?.setSelectionRange(selectionStart, selectionEnd)
          }
        }, 0)
      }
    } catch (err) {
      setError('Failed to fetch data: ' + err.message)
      console.error('API Request failed:', err)
    } finally {
      setLoading(false)
    }
  }, [tableName, page, rowsPerPage, searchQuery, columnFilters])

  // Handle search with debounce
  useEffect(() => {
    const timer = setTimeout(() => {
      fetchData()
    }, 300)
    return () => clearTimeout(timer)
  }, [searchQuery, fetchData])

  // Fetch data when table or pagination changes
  useEffect(() => {
    if (!searchQuery) {
      fetchData()
    }
  }, [tableName, page, rowsPerPage, fetchData])

  // Handle search input change
  const handleSearchChange = useCallback((e) => {
    setSearchQuery(e.target.value)
    setPage(0) // Reset to first page when searching
  }, [])

  /**
   * Pagination handlers
   */
  // Handle page change
  const handleChangePage = (event, newPage) => {
    setPage(newPage)
  }

  // Handle rows per page change
  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10))
    setPage(0)
  }

  /**
   * Delete operation handlers
   */
  // Open delete confirmation dialog
  const handleDeleteClick = (item) => {
    setSelectedItem(item)
    setDeleteDialogOpen(true)
  }

  // Execute delete operation
  const handleDelete = async () => {
    try {
      await axios.delete(API_ENDPOINTS.DATA.DELETE(tableName, selectedItem.id))
      setDeleteDialogOpen(false)
      setSelectedItem(null)
      // Refresh data after successful deletion
      fetchData()
    } catch (err) {
      setDeleteError('Failed to delete: ' + err.message)
      console.error('Delete failed:', err)
    }
  }

  // Fetch schema when component mounts
  useEffect(() => {
    const fetchSchema = async () => {
      try {
        const response = await axios.get(API_ENDPOINTS.SCHEMA.DETAIL(tableName))
        setTableSchema(response.data)
      } catch (err) {
        console.error('Failed to fetch schema:', err)
      }
    }
    fetchSchema()
  }, [tableName])

  // Initialize column visibility based on schema and first data
  useEffect(() => {
    if (data.length > 0 && tableSchema && !columnsInitialized) {
      const initialVisibility = Object.keys(data[0]).reduce((acc, key) => {
        // Check if the field exists in the schema and has hidden_in_list property
        const fieldSchema = tableSchema.fields[key]
        acc[key] = fieldSchema ? !fieldSchema.hidden_in_list : true
        return acc
      }, {})
      setColumnVisibility(initialVisibility)
      setColumnsInitialized(true)
    }
  }, [data, tableSchema, columnsInitialized])

  // Memoized visible columns with schema information
  const visibleColumns = useMemo(() => {
    if (data.length === 0) return []

    // Get all possible columns from current data
    const currentColumns = new Set(Object.keys(data[0]))

    // Merge with existing visibility settings
    const mergedVisibility = { ...columnVisibility }

    // Add any new columns that might appear in the data
    currentColumns.forEach(col => {
      if (!(col in mergedVisibility)) {
        // Check schema for new columns
        const fieldSchema = tableSchema?.fields[col]
        mergedVisibility[col] = fieldSchema ? !fieldSchema.hidden_in_list : true
      }
    })

    // Update visibility state if new columns were found
    if (Object.keys(mergedVisibility).length !== Object.keys(columnVisibility).length) {
      setColumnVisibility(mergedVisibility)
    }

    // Return only visible columns that exist in current data
    return Array.from(currentColumns)
      .filter(key => mergedVisibility[key])
      .map(key => ({
        id: key,
        label: key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' '),
        hidden_in_list: tableSchema?.fields[key]?.hidden_in_list || false
      }))
  }, [data, columnVisibility, tableSchema])

  // Column visibility handlers
  const handleColumnMenuOpen = (event) => {
    setColumnMenuAnchor(event.currentTarget)
  }

  const handleColumnMenuClose = () => {
    setColumnMenuAnchor(null)
  }

  const handleColumnVisibilityChange = (columnId) => {
    setColumnVisibility(prev => ({
      ...prev,
      [columnId]: !prev[columnId]
    }))
  }

  // Handle column filter changes
  const handleFilterChange = (columnId, value) => {
    setColumnFilters(prev => {
      const newFilters = { ...prev }
      if (value) {
        newFilters[columnId] = value
      } else {
        delete newFilters[columnId]
      }
      return newFilters
    })
    setPage(0) // Reset to first page when filter changes
  }

  // Handle filter popover
  const handleFilterClick = (event, columnId) => {
    setFilterAnchor(prev => ({
      ...prev,
      [columnId]: event.currentTarget
    }))
  }

  const handleFilterClose = (columnId) => {
    setFilterAnchor(prev => {
      const newAnchors = { ...prev }
      delete newAnchors[columnId]
      return newAnchors
    })
  }

  // Clear all filters
  const handleClearAllFilters = () => {
    setColumnFilters({})
    setPage(0)
  }

  // Loading state view
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

  // Error state view
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

  // Main component view
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
          {/* Header section with title, search, and actions */}
          <Box sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            mb: 2,
          }}>
            <Typography variant="h6" component="h2">
              {tableName.charAt(0).toUpperCase() + tableName.slice(1)}
            </Typography>

            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                inputRef={searchInputRef}
                size="small"
                placeholder="Search..."
                value={searchQuery}
                onChange={handleSearchChange}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon fontSize="small" />
                    </InputAdornment>
                  ),
                }}
              />

              <Tooltip title="Show/Hide Columns">
                <IconButton
                  onClick={handleColumnMenuOpen}
                  color="primary"
                >
                  <ViewColumnIcon />
                </IconButton>
              </Tooltip>

              {Object.keys(columnFilters).length > 0 && (
                <Tooltip title="Clear All Filters">
                  <IconButton
                    onClick={handleClearAllFilters}
                    color="primary"
                  >
                    <ClearIcon />
                  </IconButton>
                </Tooltip>
              )}

              <Button variant="contained" color="primary">
                Add
              </Button>
            </Box>
          </Box>

          {/* Column visibility menu */}
          <Menu
            anchorEl={columnMenuAnchor}
            open={Boolean(columnMenuAnchor)}
            onClose={handleColumnMenuClose}
            PaperProps={{
              sx: {
                maxHeight: 300,
                width: 200,
              }
            }}
          >
            {data.length > 0 && Object.keys(columnVisibility)
              .filter(columnId => Object.keys(data[0]).includes(columnId))
              .map(columnId => {
                const fieldSchema = tableSchema?.fields[columnId]
                return (
                  <MenuItem
                    key={columnId}
                    onClick={() => handleColumnVisibilityChange(columnId)}
                    dense
                  >
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={columnVisibility[columnId] || false}
                          onClick={(e) => e.stopPropagation()}
                          onChange={() => handleColumnVisibilityChange(columnId)}
                          size="small"
                        />
                      }
                      label={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <span>
                            {columnId.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                          </span>
                          {fieldSchema?.hidden_in_list && (
                            <Typography
                              variant="caption"
                              sx={{ color: 'text.secondary', fontStyle: 'italic' }}
                            >
                              (Hidden by default)
                            </Typography>
                          )}
                        </Box>
                      }
                      sx={{ m: 0 }}
                    />
                  </MenuItem>
                )
              })}
          </Menu>

          {/* Data table */}
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
                  <TableCell sx={{ width: '90px', whiteSpace: 'nowrap' }}>Actions</TableCell>
                  {visibleColumns.map(column => (
                    <TableCell key={column.id}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {column.label}
                        <Tooltip title="Filter Column">
                          <IconButton
                            size="small"
                            onClick={(e) => handleFilterClick(e, column.id)}
                            color={columnFilters[column.id] ? 'primary' : 'default'}
                          >
                            <FilterIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Box>
                      <Popover
                        open={Boolean(filterAnchor[column.id])}
                        anchorEl={filterAnchor[column.id]}
                        onClose={() => handleFilterClose(column.id)}
                        anchorOrigin={{
                          vertical: 'bottom',
                          horizontal: 'left',
                        }}
                        transformOrigin={{
                          vertical: 'top',
                          horizontal: 'left',
                        }}
                      >
                        <Box sx={{ p: 2, width: 250 }}>
                          <TextField
                            size="small"
                            fullWidth
                            placeholder={`Filter ${column.label}...`}
                            value={columnFilters[column.id] || ''}
                            onChange={(e) => handleFilterChange(column.id, e.target.value)}
                            InputProps={{
                              endAdornment: columnFilters[column.id] && (
                                <InputAdornment position="end">
                                  <IconButton
                                    size="small"
                                    onClick={() => handleFilterChange(column.id, '')}
                                  >
                                    <ClearIcon fontSize="small" />
                                  </IconButton>
                                </InputAdornment>
                              ),
                            }}
                          />
                        </Box>
                      </Popover>
                    </TableCell>
                  ))}
                </TableRow>
              </TableHead>

              <TableBody>
                {data.map((row) => (
                  <TableRow key={row.id} hover>
                    <TableCell sx={{
                      width: '90px',
                      whiteSpace: 'nowrap',
                      p: '4px 8px',
                    }}>
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        <IconButton
                          size="small"
                          color="primary"
                          onClick={() => navigate(`/data/request/${tableName}/${row.id}`)}
                        >
                          <EditIcon fontSize="small" />
                        </IconButton>

                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => handleDeleteClick(row)}
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Box>
                    </TableCell>

                    {/* Data cells */}
                    {visibleColumns.map(column => (
                      <TableCell
                        key={column.id}
                        onClick={column.id === 'id' ? () => navigate(`/data/request/${tableName}/${row.id}`) : undefined}
                        sx={column.id === 'id' ? {
                          cursor: 'pointer',
                          color: 'primary.main',
                          '&:hover': {
                            textDecoration: 'underline',
                          },
                        } : undefined}
                      >
                        {row[column.id] === null ? '-' : String(row[column.id])}
                      </TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Pagination controls */}
          <TablePagination
            component="div"
            count={-1}
            page={page}
            onPageChange={handleChangePage}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={handleChangeRowsPerPage}
            rowsPerPageOptions={[10, 25, 50]}
          />
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

      {/* Error notification */}
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

export default DataTable