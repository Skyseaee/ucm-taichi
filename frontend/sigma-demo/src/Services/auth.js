import axios from 'axios';

const API_URL = 'http://localhost8000/api/auth';

export const login = async (credentials) => {
  const response = await axios.post(`${API_URL}/login`, credentials, {
    withCredentials: true
  });
  return response.data;
};

export const register = async (userData) => {
  const response = await axios.post(`${API_URL}/register`, userData);
  return response.data;
};

export const logout = async () => {
  await axios.post(`${API_URL}/logout`, {}, { withCredentials: true });
};

export const checkAuth = async () => {
  const response = await axios.get(`${API_URL}/check_auth`, {
    withCredentials: true
  });
  return response.data;
};