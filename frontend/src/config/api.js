const API_BASE_URL = '/api/v1'

export const API_ENDPOINTS = {
  SCHEMA: {
    REQUEST: `${API_BASE_URL}/schema/request`,
    DETAIL: (tableName) => `${API_BASE_URL}/schema/detail/${tableName}`,
  },
  DATA: {
    REQUEST: (tableName) => `${API_BASE_URL}/data/request/${tableName}`,
    DETAIL: (tableName, id) => `${API_BASE_URL}/data/detail/${tableName}/${id}`,
    DELETE: (tableName, id) => `${API_BASE_URL}/data/detail/${tableName}/${id}`,
  },
  PLUGINS: {
    REPORTERS: `${API_BASE_URL}/plugins/reporters`,
  },
  REPORT: {
    GENERATE: (reporterName) => `${API_BASE_URL}/report/${reporterName}`,
  },
  INGEST: {
    PLUGINS: `${API_BASE_URL}/ingest/plugins`,
    UPLOAD: (ingestorName) => `${API_BASE_URL}/ingest/${ingestorName}`,
  },
}
