import { defineStore } from 'pinia';
import api from '../api';
import router from '../router';

export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: null,
        token: localStorage.getItem('token') || null,
        error: null
    }),
    actions: {
        async login(username, password) {
            try {
                const formData = new FormData();
                formData.append('username', username);
                formData.append('password', password);
                
                const response = await api.post('/auth/token', formData);
                this.token = response.data.access_token;
                localStorage.setItem('token', this.token);
                await this.fetchUser();
                router.push('/');
            } catch (error) {
                this.error = error.response?.data?.detail || 'Login failed';
                throw error;
            }
        },
        async register(username, email, password) {
            try {
                console.log('Attempting registration:', { username, email });
                const response = await api.post('/auth/register', { username, email, password });
                console.log('Registration success:', response.data);
                await this.login(username, password);
            } catch (error) {
                console.error('Registration error details:', error);
                if (error.response) {
                    // The request was made and the server responded with a status code
                    // that falls out of the range of 2xx
                    this.error = error.response.data.detail || `Server error: ${error.response.status}`;
                } else if (error.request) {
                    // The request was made but no response was received
                    this.error = 'No response from server. Please check if backend is running.';
                } else {
                    // Something happened in setting up the request that triggered an Error
                    this.error = `Request setup error: ${error.message}`;
                }
                throw error;
            }
        },
        async fetchUser() {
            try {
                const response = await api.get('/auth/me');
                this.user = response.data;
            } catch (error) {
                this.logout();
            }
        },
        async updateProfile(userData) {
            const response = await api.put('/auth/me', userData);
            this.user = response.data;
        },
        async uploadAvatar(file) {
            const formData = new FormData();
            formData.append('file', file);
            const response = await api.post('/auth/me/avatar', formData);
            this.user = response.data;
        },
        logout() {
            this.user = null;
            this.token = null;
            localStorage.removeItem('token');
            router.push('/login');
        }
    }
});
