const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  SCHEMA: {
    REQUEST: `${API_BASE_URL}/api/v1/schema/names`,
    TABLE: (tableName: string) => `${API_BASE_URL}/api/v1/schema/entity/${tableName}`,
  },
  DATA: {
    REQUEST: (tableName: string) => `${API_BASE_URL}/data/request/${tableName}`,
    DETAIL: (tableName: string, id: string | number) => `${API_BASE_URL}/data/request/${tableName}/${id}`,
  },
  INGEST: {
    UPLOAD: `${API_BASE_URL}/ingest/upload`,
    STATUS: `${API_BASE_URL}/ingest/status`,
  },
  REPORT: {
    GENERATE: `${API_BASE_URL}/report/generate`,
    STATUS: `${API_BASE_URL}/report/status`,
  },
};
