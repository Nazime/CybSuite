import React, { useState, useEffect, useMemo } from 'react'
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
} from '@mui/material'
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
} from '@mui/icons-material'
import TableSidebar from './TableSidebar'
import { API_ENDPOINTS } from '../config/api'

const DataTable = () => {
  const { tableName } = useParams()
  const navigate = useNavigate()
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const response = await axios.get(`${API_ENDPOINTS.DATA.REQUEST(tableName)}?skip=${page * rowsPerPage}&limit=${rowsPerPage}`)
        setData(response.data)
        setError(null)
      } catch (err) {
        setError('Failed to fetch data: ' + err.message)
        console.error('API Request failed:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [tableName, page, rowsPerPage])

  const handleChangePage = (event, newPage) => {
    setPage(newPage)
  }

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10))
    setPage(0)
  }

  const columns = useMemo(() => {
    if (data.length === 0) return []
    return Object.keys(data[0]).map(key => ({
      id: key,
      label: key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' '),
    }))
  }, [data])

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

  const filteredData = data.filter(row =>
    Object.values(row).some(value =>
      String(value).toLowerCase().includes(searchQuery.toLowerCase())
    )
  )

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
            mb: 2,
          }}>
            <Typography variant="h6" component="h2">
              {tableName.charAt(0).toUpperCase() + tableName.slice(1)}
            </Typography>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                size="small"
                placeholder="Search..."
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
              <Button variant="contained" color="primary">
                Add
              </Button>
            </Box>
          </Box>

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
                  <TableCell>Actions</TableCell>
                  {columns.map(column => (
                    <TableCell key={column.id}>{column.label}</TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredData.map((row, index) => (
                  <TableRow key={index} hover>
                    <TableCell>
                      <IconButton
                        size="small"
                        color="primary"
                        onClick={() => navigate(`/data/request/${tableName}/${row.id}`)}
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                      <IconButton size="small" color="error">
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </TableCell>
                    {columns.map(column => (
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
    </Box>
  )
}

export default DataTable