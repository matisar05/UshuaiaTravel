import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
    baseURL: API_URL,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
});

apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 429) {
            console.warn('Rate limit exceeded');
        }
        return Promise.reject(error);
    }
);
