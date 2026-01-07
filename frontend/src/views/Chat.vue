<script setup>
import { ref, onMounted, nextTick, watch, computed } from 'vue';
import { useChatStore } from '../stores/chat';
import { useAuthStore } from '../stores/auth';
import { marked } from 'marked';
import markedKatex from 'marked-katex-extension';
import DOMPurify from 'dompurify';
import StarBackground from '../components/StarBackground.vue';
import 'katex/dist/katex.min.css';

// Configure marked with katex
marked.use(markedKatex({
  throwOnError: false
}));

const chatStore = useChatStore();
const authStore = useAuthStore();
const inputMessage = ref('');
const attachedImages = ref([]);
const attachedFile = ref(null);
const selectedModel = ref('qwen-plus');
const chatContainer = ref(null);

// Sidebar Editing
const editingSessionId = ref(null);
const editingTitle = ref('');
const titleInput = ref(null);

// Typewriter
const headerText = ref('AI Chat');
const headerClass = ref('text-white');
const typewriterTexts = computed(() => [
    'AI Chat',
    `Hello ${authStore.user?.username || 'User'}!`,
    'Ask me anything...',
    'Multi-modal Support'
]);
let typewriterIndex = 0;
let charIndex = 0;
let isDeleting = false;

const typeWriter = () => {
    const currentText = typewriterTexts.value[typewriterIndex];
    if (isDeleting) {
        headerText.value = currentText.substring(0, charIndex - 1);
        charIndex--;
    } else {
        headerText.value = currentText.substring(0, charIndex + 1);
        charIndex++;
    }

    let typeSpeed = 100;
    if (isDeleting) typeSpeed /= 2;

    if (!isDeleting && charIndex === currentText.length) {
        isDeleting = true;
        typeSpeed = 2000;
        // Cycle colors
        const colors = ['text-white', 'text-blue-400', 'text-green-400', 'text-purple-400'];
        headerClass.value = colors[typewriterIndex % colors.length];
    } else if (isDeleting && charIndex === 0) {
        isDeleting = false;
        typewriterIndex = (typewriterIndex + 1) % typewriterTexts.value.length;
        typeSpeed = 500;
        headerClass.value = 'text-white';
    }

    setTimeout(typeWriter, typeSpeed);
};

onMounted(async () => {
    if (authStore.token) {
        await chatStore.fetchSessions();
        await authStore.fetchUser(); // Ensure user data is fresh
    }
    typeWriter();
});

const startEdit = (session) => {
    editingSessionId.value = session.id;
    editingTitle.value = session.title;
    nextTick(() => {
         // Focus input logic needs to handle v-for refs
         // Simplification: just rely on autofocus or click
    });
};

const saveTitle = async (sessionId) => {
    if (editingTitle.value.trim()) {
        await chatStore.updateSessionTitle(sessionId, editingTitle.value);
    }
    editingSessionId.value = null;
};

const scrollToBottom = async () => {
    await nextTick();
    if (chatContainer.value) {
        chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
    }
};

watch(() => chatStore.messages, () => {
    scrollToBottom();
}, { deep: true });

const sendMessage = async () => {
    if (!inputMessage.value.trim() && attachedImages.value.length === 0 && !attachedFile.value) return;
    
    const content = inputMessage.value;
    inputMessage.value = '';
    const images = [...attachedImages.value];
    const fileContext = attachedFile.value?.content;

    attachedImages.value = [];
    attachedFile.value = null;
    
    await chatStore.sendMessage(content, selectedModel.value, images, fileContext);
};

const handleFileUpload = async (event) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('http://localhost:8000/api/v1/chat/upload', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: formData
            });
            const data = await response.json();
            
            // Handle text content
            if (data.result.text) {
                 // Append text if multiple files have text? Or just overwrite?
                 // For now, let's append if there's already content
                 if (attachedFile.value) {
                     attachedFile.value.content += "\n\n" + data.result.text;
                     attachedFile.value.name += ", " + data.filename;
                 } else {
                     attachedFile.value = {
                        name: data.filename,
                        content: data.result.text
                    };
                 }
            }
            
            // Handle images
            if (data.result.images && data.result.images.length > 0) {
                data.result.images.forEach(img => {
                    attachedImages.value.push(img.content);
                });
                selectedModel.value = 'qwen-vl-max';
            }
            
            if (!data.result.text && (!data.result.images || data.result.images.length === 0)) {
                 if (data.result.error) {
                     alert(`Upload error for ${file.name}: ` + data.result.error);
                 }
            }

        } catch (error) {
            console.error(`File upload failed for ${file.name}:`, error);
            alert(`File upload failed for ${file.name}`);
        }
    }
    
    event.target.value = ''; // Reset input
};

const renderMarkdown = (content) => {
    return DOMPurify.sanitize(marked.parse(content, { breaks: true }));
};

const selectSession = async (sessionId) => {
    await chatStore.loadSession(sessionId);
};

const createNewChat = async () => {
    await chatStore.createSession();
};
</script>

<template>
    <StarBackground />
    <div class="flex h-screen">
        <!-- Sidebar -->
        <div class="w-64 bg-gray-900/80 backdrop-blur-md border-r border-white/10 text-white flex flex-col">
            <div class="p-4 border-b border-white/10 flex justify-between items-center h-16">
                <span :class="['font-bold transition-colors duration-500 text-lg', headerClass]">{{ headerText }}<span class="animate-pulse">|</span></span>
                <button @click="createNewChat" class="text-sm bg-blue-600/80 px-2 py-1 rounded hover:bg-blue-600 shadow border border-blue-400/30 transition-all">+</button>
            </div>
            <div class="flex-1 overflow-y-auto custom-scrollbar">
                <div v-for="session in chatStore.sessions" :key="session.id">
                    <div v-if="editingSessionId === session.id" class="p-2">
                        <input v-model="editingTitle" @blur="saveTitle(session.id)" @keydown.enter="saveTitle(session.id)" 
                               class="bg-gray-700/50 text-white px-2 py-1 rounded w-full text-sm outline-none border border-blue-500/50" 
                               autofocus />
                    </div>
                    <div v-else 
                         @click="selectSession(session.id)"
                         :class="['p-3 cursor-pointer hover:bg-white/10 flex justify-between items-center group transition-colors', chatStore.currentSession?.id === session.id ? 'bg-white/10 border-r-2 border-blue-500' : '']">
                        <span class="truncate text-sm flex-1 text-gray-200">{{ session.title }}</span>
                        <button @click.stop="startEdit(session)" class="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-white px-1 transition-opacity">✎</button>
                    </div>
                </div>
            </div>
            <div class="p-4 border-t border-white/10 flex justify-between items-center bg-black/20">
                <div class="flex items-center cursor-pointer hover:bg-white/5 p-2 -ml-2 rounded flex-1 transition truncate" @click="$router.push('/profile')">
                    <div class="w-8 h-8 rounded-full bg-gray-700 flex-shrink-0 flex items-center justify-center mr-2 overflow-hidden border border-gray-600">
                        <img v-if="authStore.user?.avatar_url" :src="authStore.user.avatar_url" class="w-full h-full object-cover" />
                        <span v-else class="text-sm font-bold text-gray-300">{{ authStore.user?.username?.charAt(0).toUpperCase() }}</span>
                    </div>
                    <div class="flex flex-col truncate">
                         <span class="text-sm font-medium truncate text-gray-200">{{ authStore.user?.username }}</span>
                         <span class="text-xs text-gray-500">My Profile</span>
                    </div>
                </div>
                <button @click="authStore.logout()" class="ml-2 text-gray-400 hover:text-white p-2 rounded hover:bg-white/10 transition" title="Logout">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                </button>
            </div>
        </div>

        <!-- Chat Area -->
        <div class="flex-1 flex flex-col relative z-0">
            <header class="bg-gray-900/60 backdrop-blur-md shadow-lg p-4 flex justify-between items-center z-10 border-b border-white/5">
                <h2 class="text-lg font-semibold text-white">{{ chatStore.currentSession?.title || 'New Chat' }}</h2>
                <div class="relative">
                    <select v-model="selectedModel" class="appearance-none bg-gray-800/80 border border-gray-600 hover:border-gray-500 text-white px-4 py-2 pr-8 rounded shadow leading-tight focus:outline-none focus:shadow-outline cursor-pointer transition-colors">
                        <option value="qwen-plus">Qwen Plus</option>
                        <option value="qwen-vl-max">Qwen VL Max</option>
                        <option value="deepseek-chat">Deepseek Chat</option>
                    </select>
                    <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-400">
                        <svg class="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/></svg>
                    </div>
                </div>
            </header>

            <div class="flex-1 overflow-y-auto p-4 custom-scrollbar" ref="chatContainer">
                <div v-if="!chatStore.currentSession" class="flex items-center justify-center h-full text-gray-400 bg-black/10 rounded-xl m-4 backdrop-blur-sm border border-white/5">
                    <div class="text-center">
                        <div class="text-4xl mb-4">✨</div>
                        Select a chat or start a new one to explore the universe.
                    </div>
                </div>
                <div v-else class="space-y-6">
                    <div v-for="(msg, index) in chatStore.messages" :key="index" 
                         :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']">
                        <div :class="['max-w-3xl rounded-2xl p-4 shadow-xl backdrop-blur-sm border border-white/5', 
                                     msg.role === 'user' ? 'bg-blue-600/90 text-white' : 'bg-gray-800/80 text-gray-100']">
                            <div v-if="msg.role === 'user'" class="prose prose-invert max-w-none" v-html="renderMarkdown(msg.content)"></div>
                            <div v-else class="prose prose-invert max-w-none" v-html="renderMarkdown(msg.content)"></div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="bg-gray-900/80 backdrop-blur-md border-t border-white/10">
                <div v-if="attachedImages.length > 0 || attachedFile" class="p-2 bg-black/20 border-b border-white/5 flex flex-wrap gap-2">
                    <div v-for="(img, idx) in attachedImages" :key="idx" class="relative group">
                        <img :src="img" class="h-20 w-auto rounded-lg border border-white/20 shadow-sm" />
                        <button @click="attachedImages.splice(idx, 1)" class="absolute -top-1 -left-1 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs shadow hover:bg-red-600 transition">x</button>
                    </div>
                    <div v-if="attachedFile" class="flex items-center bg-blue-900/50 text-blue-200 px-3 py-1 rounded-full text-sm border border-blue-500/30">
                        <span class="mr-2 truncate max-w-xs">📄 {{ attachedFile.name }}</span>
                        <button @click="attachedFile = null" class="font-bold hover:text-red-400 transition">×</button>
                    </div>
                </div>
                <div class="p-4 flex space-x-2">
                    <label class="cursor-pointer text-gray-400 hover:text-blue-400 p-2 transition-colors">
                        <input type="file" class="hidden" @change="handleFileUpload" multiple accept=".txt,.pdf,.docx,.jpg,.jpeg,.png,.gif,.bmp,.webp">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                        </svg>
                    </label>
                    <textarea v-model="inputMessage" @keydown.enter.prevent="sendMessage"
                              class="flex-1 bg-gray-800/50 border border-gray-600 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-blue-500/50 resize-none text-white placeholder-gray-500 transition-all"
                              rows="1" placeholder="Type a message to the stars..."></textarea>
                    <button @click="sendMessage" class="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-2 rounded-xl hover:from-blue-500 hover:to-blue-600 shadow-lg border border-blue-400/20 transition-all transform hover:scale-105">Send</button>
                </div>
            </div>
        </div>
    </div>
</template>
