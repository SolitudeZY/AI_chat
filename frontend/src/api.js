import axios from 'axios';
import router from './router';

const api = axios.create({
    baseURL: 'http://localhost:8000/api/v1',
});

api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && (error.response.status === 401 || error.response.status === 403)) {
            localStorage.removeItem('token');
            router.push('/login');
        }
        return Promise.reject(error);
    }
);

export default api;
