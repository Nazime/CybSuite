import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Container,
} from '@mui/material'
import {
  TableChart as TableChartIcon,
  Schema as SchemaIcon,
  CloudUpload as CloudUploadIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material'
import './App.css'
import DataTable from './components/DataTable'
import DataView from './components/DataView'
import DataDetail from './components/DataDetail'
import SchemaView from './components/SchemaView'
import SchemaTable from './components/SchemaTable'
import IngestView from './components/IngestView'
import ReportView from './components/ReportView'
import { SidebarProvider } from './contexts/SidebarContext'

function App() {
  return (
    <SidebarProvider>
      <Router>
        <Box sx={{ flexGrow: 1 }}>
          <AppBar position="static">
            <Toolbar>
              <Typography
                variant="h6"
                component={Link}
                to="/"
                sx={{
                  mr: 4,
                  textDecoration: 'none',
                  color: 'inherit',
                  '&:hover': {
                    color: 'rgba(255, 255, 255, 0.8)',
                  },
                }}
              >
                CybSuite
              </Typography>
              <Button
                color="inherit"
                component={Link}
                to="/data"
                startIcon={<TableChartIcon />}
                sx={{ mr: 2 }}
              >
                Data
              </Button>
              <Button
                color="inherit"
                component={Link}
                to="/schema"
                startIcon={<SchemaIcon />}
                sx={{ mr: 2 }}
              >
                Schema
              </Button>
              <Button
                color="inherit"
                component={Link}
                to="/ingest"
                startIcon={<CloudUploadIcon />}
                sx={{ mr: 2 }}
              >
                Ingest
              </Button>
              <Button
                color="inherit"
                component={Link}
                to="/report"
                startIcon={<AssessmentIcon />}
              >
                Report
              </Button>
            </Toolbar>
          </AppBar>

          <Box sx={{ mt: 0 }}>
            <Routes>
              <Route path="/" element={
                <Container sx={{ mt: 4 }}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h3" component="h1" gutterBottom>
                      Welcome to CybSuite
                    </Typography>
                    <Typography variant="h5" component="h2" color="text.secondary">
                      Your comprehensive penetration testing management platform
                    </Typography>
                  </Box>
                </Container>
              } />
              <Route path="/data" element={<DataView />} />
              <Route path="/data/request/:tableName" element={<DataTable />} />
              <Route path="/data/request/:tableName/:id" element={<DataDetail />} />
              <Route path="/schema" element={<SchemaView />} />
              <Route path="/schema/:tableName" element={<SchemaTable />} />
              <Route path="/ingest" element={<IngestView />} />
              <Route path="/report" element={<ReportView />} />
            </Routes>
          </Box>
        </Box>
      </Router>
    </SidebarProvider>
  )
}

export default App