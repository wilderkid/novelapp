import axios from 'axios';

const API_URL = 'http://localhost:9009/api';

// AI Provider services
export const getProviders = (projectId) => {
  return axios.get(`${API_URL}/projects/${projectId}/ai-providers`);
};

export const createProvider = (projectId, data) => {
  return axios.post(`${API_URL}/projects/${projectId}/ai-providers`, data);
};

export const updateProvider = (providerId, data) => {
  return axios.put(`${API_URL}/ai-providers/${providerId}`, data);
};

export const deleteProvider = (providerId) => {
  return axios.delete(`${API_URL}/ai-providers/${providerId}`);
};

// AI Model services
export const getModels = (providerId) => {
  return axios.get(`${API_URL}/ai-providers/${providerId}/ai-models`);
};

export const createModel = (providerId, data) => {
  return axios.post(`${API_URL}/ai-providers/${providerId}/ai-models`, data);
};

export const updateModel = (modelId, data) => {
  return axios.put(`${API_URL}/ai-models/${modelId}`, data);
};

export const deleteModel = (modelId) => {
  return axios.delete(`${API_URL}/ai-models/${modelId}`);
};
