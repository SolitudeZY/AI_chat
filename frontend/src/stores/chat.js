import { defineStore } from 'pinia';
import api from '../api';

export const useChatStore = defineStore('chat', {
    state: () => ({
        sessions: [],
        currentSession: null,
        messages: [],
        loading: false
    }),
    actions: {
        async fetchSessions() {
            const response = await api.get('/chat/sessions');
            this.sessions = response.data;
        },
        async createSession(title = 'New Chat') {
            const response = await api.post('/chat/sessions', { title });
            this.sessions.unshift(response.data);
            this.currentSession = response.data;
            this.messages = [];
        },
        async loadSession(sessionId) {
            const response = await api.get(`/chat/sessions/${sessionId}`);
            this.currentSession = response.data;
            this.messages = response.data.messages || [];
        },
        async sendMessage(content, model, images = [], fileContext = null) {
            if (!this.currentSession) {
                await this.createSession();
            }
            
            // Move current session to top locally
            const sessionIndex = this.sessions.findIndex(s => s.id === this.currentSession.id);
            if (sessionIndex > 0) {
                const session = this.sessions.splice(sessionIndex, 1)[0];
                this.sessions.unshift(session);
            }
            
            // Add user message immediately
            let displayContent = content + (fileContext ? '\n\n[Attached Document Context]' : '');
            if (images && images.length > 0) {
                 images.forEach((img, idx) => {
                     displayContent += `\n\n![Image ${idx+1}](${img})`;
                 });
            }
            
            const userMsg = { 
                role: 'user', 
                content: displayContent, 
                created_at: new Date().toISOString() 
            };
            this.messages.push(userMsg);

            // Create placeholder for assistant message
            const assistantMsg = { role: 'assistant', content: '', created_at: new Date().toISOString() };
            this.messages.push(assistantMsg);
            const assistantMsgIndex = this.messages.length - 1;

            try {
                const response = await fetch(`http://localhost:8000/api/v1/chat/sessions/${this.currentSession.id}/messages`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    },
                    body: JSON.stringify({ content, model, images, file_context: fileContext })
                });

                const reader = response.body.getReader();
                const decoder = new TextDecoder();

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    const chunk = decoder.decode(value);
                    this.messages[assistantMsgIndex].content += chunk;
                }

                // Refresh session title (background task might have updated it)
                const sessionRes = await api.get(`/chat/sessions/${this.currentSession.id}`);
                if (sessionRes.data.title !== 'New Chat') {
                    this.currentSession.title = sessionRes.data.title;
                    const sessionInList = this.sessions.find(s => s.id === this.currentSession.id);
                    if (sessionInList) sessionInList.title = sessionRes.data.title;
                }

            } catch (error) {
                console.error('Error sending message:', error);
                this.messages[assistantMsgIndex].content += "\n[Error generating response]";
            }
        },
        async updateSessionTitle(sessionId, title) {
            const response = await api.patch(`/chat/sessions/${sessionId}`, { title });
            const session = this.sessions.find(s => s.id === sessionId);
            if (session) {
                session.title = response.data.title;
            }
            if (this.currentSession && this.currentSession.id === sessionId) {
                this.currentSession.title = response.data.title;
            }
        },
        async generateSessionSummary(sessionId) {
            const response = await api.post(`/chat/sessions/${sessionId}/summary`);
            const session = this.sessions.find(s => s.id === sessionId);
            if (session) {
                session.title = response.data.title;
            }
            if (this.currentSession && this.currentSession.id === sessionId) {
                this.currentSession.title = response.data.title;
            }
        }
    }
});
