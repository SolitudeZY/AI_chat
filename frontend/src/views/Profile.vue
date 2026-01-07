<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

const username = ref('');
const email = ref('');
const bio = ref('');
const message = ref('');

onMounted(() => {
    if (authStore.user) {
        username.value = authStore.user.username;
        email.value = authStore.user.email;
        bio.value = authStore.user.bio || '';
    }
});

const handleUpdate = async () => {
    try {
        await authStore.updateProfile({
            username: username.value,
            email: email.value,
            bio: bio.value
        });
        message.value = 'Profile updated successfully!';
        setTimeout(() => message.value = '', 3000);
    } catch (e) {
        console.error(e);
        message.value = 'Error updating profile';
    }
};

const handleAvatarUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    
    try {
        await authStore.uploadAvatar(file);
    } catch (e) {
        console.error(e);
        alert('Avatar upload failed');
    }
};

const goBack = () => {
    router.push('/');
};

const logout = () => {
    authStore.logout();
};
</script>

<template>
    <div class="min-h-screen bg-gray-100 p-8">
        <div class="max-w-2xl mx-auto bg-white rounded-lg shadow p-6">
            <div class="flex justify-between items-center mb-6">
                <h1 class="text-2xl font-bold">Edit Profile</h1>
                <div class="space-x-4">
                    <button @click="logout" class="text-red-600 hover:text-red-800">Logout</button>
                    <button @click="goBack" class="text-gray-600 hover:text-gray-900">Back to Chat</button>
                </div>
            </div>
            
            <div class="flex flex-col items-center mb-8">
                <div class="relative group cursor-pointer w-24 h-24 mb-4">
                    <img :src="authStore.user?.avatar_url || 'https://via.placeholder.com/150'" 
                         class="w-full h-full rounded-full object-cover border-2 border-gray-200" />
                    <label class="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity">
                        <input type="file" class="hidden" @change="handleAvatarUpload" accept="image/*">
                        <span>Change</span>
                    </label>
                </div>
                <h2 class="text-xl font-semibold">{{ authStore.user?.username }}</h2>
            </div>

            <form @submit.prevent="handleUpdate" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700">Username</label>
                    <input v-model="username" type="text" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">Email</label>
                    <input v-model="email" type="email" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">Bio</label>
                    <textarea v-model="bio" rows="3" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border"></textarea>
                </div>
                
                <div class="flex items-center justify-between pt-4">
                    <p v-if="message" :class="message.includes('Error') ? 'text-red-500' : 'text-green-500'">{{ message }}</p>
                    <button type="submit" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">Save Changes</button>
                </div>
            </form>
        </div>
    </div>
</template>
