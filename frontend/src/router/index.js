import { createRouter, createWebHistory } from 'vue-router';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';
import Chat from '../views/Chat.vue';
import Profile from '../views/Profile.vue';

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: Login,
        meta: { title: 'Login - AI Chat' }
    },
    {
        path: '/register',
        name: 'Register',
        component: Register,
        meta: { title: 'Register - AI Chat' }
    },
    {
        path: '/',
        name: 'Chat',
        component: Chat,
        meta: { requiresAuth: true, title: 'Chat - AI Chat' }
    },
    {
        path: '/profile',
        name: 'Profile',
        component: Profile,
        meta: { requiresAuth: true, title: 'Profile - AI Chat' }
    }
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

router.beforeEach((to, from, next) => {
    document.title = to.meta.title || 'AI Chat';
    const isAuthenticated = localStorage.getItem('token');
    if (to.meta.requiresAuth && !isAuthenticated) {
        next('/login');
    } else {
        next();
    }
});

export default router;
