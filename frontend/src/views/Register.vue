<script setup>
import { ref } from 'vue';
import { useAuthStore } from '../stores/auth';
import StarBackground from '../components/StarBackground.vue';

const username = ref('');
const email = ref('');
const password = ref('');
const authStore = useAuthStore();

const handleRegister = async () => {
    try {
        await authStore.register(username.value, email.value, password.value);
    } catch (e) {
        console.error(e);
    }
};
</script>

<template>
    <StarBackground />
    <div class="flex items-center justify-center min-h-screen">
        <div class="px-8 py-6 mt-4 text-left bg-white/10 backdrop-blur-md border border-white/20 shadow-xl rounded-2xl w-full max-w-md text-white">
            <h3 class="text-3xl font-bold text-center mb-6 text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-blue-400">Join Us</h3>
            <form @submit.prevent="handleRegister">
                <div class="mt-4 space-y-4">
                    <div>
                        <label class="block text-gray-200 text-sm font-medium mb-1" for="username">Username</label>
                        <input v-model="username" type="text" placeholder="Choose a username"
                            class="w-full px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-white placeholder-gray-400 transition-all">
                    </div>
                    <div>
                        <label class="block text-gray-200 text-sm font-medium mb-1" for="email">Email</label>
                        <input v-model="email" type="email" placeholder="Enter your email"
                            class="w-full px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-white placeholder-gray-400 transition-all">
                    </div>
                    <div>
                        <label class="block text-gray-200 text-sm font-medium mb-1" for="password">Password</label>
                        <input v-model="password" type="password" placeholder="Create a password"
                            class="w-full px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-white placeholder-gray-400 transition-all">
                    </div>
                    <div class="flex items-center justify-between pt-4">
                        <button class="w-full px-6 py-3 text-white bg-gradient-to-r from-green-600 to-blue-600 rounded-lg hover:from-green-700 hover:to-blue-700 transform hover:scale-[1.02] transition-all duration-200 font-medium shadow-lg">
                            Create Account
                        </button>
                    </div>
                    <div class="text-center mt-4">
                        <span class="text-sm text-gray-400">Already have an account? </span>
                        <router-link to="/login" class="text-sm text-green-400 hover:text-green-300 hover:underline">Log in</router-link>
                    </div>
                    <p v-if="authStore.error" class="mt-2 text-red-400 text-sm text-center bg-red-900/20 py-1 rounded">{{ authStore.error }}</p>
                </div>
            </form>
        </div>
    </div>
</template>
