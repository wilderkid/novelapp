import axios from 'axios';

const API_URL = '/api';

// Generic resource handler
const resourceApi = (resourceName, pluralName) => ({
  getAll: (projectId) => axios.get(`${API_URL}/projects/${projectId}/${pluralName}`),
  get: (id) => axios.get(`${API_URL}/${pluralName}/${id}`),
  create: (projectId, data) => axios.post(`${API_URL}/projects/${projectId}/${pluralName}`, data),
  update: (id, data) => axios.put(`${API_URL}/${pluralName}/${id}`, data),
  delete: (id) => axios.delete(`${API_URL}/${pluralName}/${id}`),
  reorder: (ids) => axios.put(`${API_URL}/${pluralName}/reorder`, ids),
});

export const worldviewService = {
  get: (projectId) => axios.get(`${API_URL}/projects/${projectId}/worldview`),
  update: (projectId, data) => axios.put(`${API_URL}/projects/${projectId}/worldview`, data),
};

export const characterService = resourceApi('rpg_character', 'rpg_characters');
export const organizationService = resourceApi('organization', 'organizations');
export const supernaturalPowerService = resourceApi('supernatural_power', 'supernatural_powers');
export const weaponService = resourceApi('weapon', 'weapons');
export const dungeonService = resourceApi('dungeon', 'dungeons');
