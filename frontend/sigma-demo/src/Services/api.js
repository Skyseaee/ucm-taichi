import axios from 'axios';

const API_URL = 'http://localhost:8080/api';

export const uploadGraph = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await axios.post(`${API_URL}/graphs`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    withCredentials: true
  });
  return response.data;
};

export const updateEdge = async (edgeId, data) => {
  const response = await axios.put(`${API_URL}/edges/${edgeId}`, data, {
    withCredentials: true
  });
  return response.data;
};