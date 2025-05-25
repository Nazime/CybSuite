import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://127.0.0.1:2501',
        changeOrigin: true,
        secure: false,
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('Proxy error details:', {
              message: err.message,
              code: err.code,
              syscall: err.syscall,
              hostname: err.hostname,
              port: err.port
            });
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log('Sending Request to backend:', {
              method: req.method,
              url: req.url,
              targetUrl: proxyReq.path,
              headers: proxyReq.getHeaders()
            });
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log('Received Response from backend:', {
              statusCode: proxyRes.statusCode,
              url: req.url,
              headers: proxyRes.headers
            });
          });
        },
      }
    }
  }
})
