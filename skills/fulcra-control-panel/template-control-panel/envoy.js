document.addEventListener('alpine:init', () => {
    // Detect if we are running locally based on hostname
    const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    
    if (isLocal) {
        // Reveal local-only components
        document.querySelectorAll('.local-only').forEach(el => {
            el.classList.remove('local-only');
        });
    }

    Alpine.data('fileBrowser', () => ({
        currentPath: '',
        folders: [],
        files: [],
        loading: false,
        error: '',

        get breadcrumbs() {
            if (!this.currentPath) return [];
            const parts = this.currentPath.split('/').filter(p => p);
            let pathAcc = '';
            return parts.map(part => {
                pathAcc += part + '/';
                return { name: part, path: pathAcc };
            });
        },

        async init() {
            if (!isLocal) return;
            await this.loadDirectory('');
        },

        async navigate(path) {
            await this.loadDirectory(path);
        },

        async loadDirectory(path) {
            this.loading = true;
            this.error = '';
            this.folders = [];
            this.files = [];
            this.currentPath = path;

            try {
                const response = await fetch('/api/files?path=' + encodeURIComponent(path));
                if (!response.ok) throw new Error('Failed to fetch directory');
                const result = await response.json();
                this.folders = result.folders || [];
                this.files = result.files || [];
                this.currentPath = result.currentPath || '';
            } catch (err) {
                this.error = 'Unable to scan directory.';
                console.error(err);
            } finally {
                this.loading = false;
            }
        }
    }));

    Alpine.data('chatEnvoy', () => ({
        messages: [],
        input: '',
        isTyping: false,
        pollInterval: null,

        async init() {
            if (!isLocal) return; // Do not attempt to fetch on public static hosts
            
            await this.fetchMessages();
            // Start polling for new messages from the agent
            this.pollInterval = setInterval(() => this.fetchMessages(), 5000);
        },

        async fetchMessages() {
            try {
                // Fetch the chat history from the Python server
                const response = await fetch('/api/chat');
                if (response.ok) {
                    const result = await response.json();
                    if (result.messages && result.messages.length > this.messages.length) {
                        this.messages = result.messages;
                        this.scrollToBottom();
                    }
                    // Show typing dots only if the agent is actively processing
                    this.isTyping = result.agent_processing || false;
                }
            } catch (err) {
                console.warn('Could not establish connection to local relay.');
                this.isTyping = false;
            }
        },

        async sendMessage() {
            if (!this.input.trim()) return;

            const userMessage = this.input;
            // Optimistically add to UI
            this.messages.push({ role: 'user', text: userMessage });
            this.input = '';
            
            // Reset textarea height
            if (this.$refs.chatInput) {
                this.$refs.chatInput.style.height = 'auto';
            }
            
            this.scrollToBottom();

            try {
                // We POST to our local Python server to append to history
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: userMessage })
                });
                
                if (response.ok) {
                    const result = await response.json();
                    if (result.messages && result.messages.length > 0) {
                        this.messages.push(...result.messages);
                    }
                    // Fetch all messages to ensure consistency and update typing status
                    await this.fetchMessages();
                } else {
                    this.messages.push({ role: 'system', text: 'Error: The local relay failed to respond.' });
                }
            } catch (err) {
                this.messages.push({ role: 'system', text: 'Error: Cannot reach the local relay. Ensure the Python server is running.' });
            } finally {
                this.scrollToBottom();
            }
        },

        handleKeydown(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        },

        scrollToBottom() {
            this.$nextTick(() => {
                const win = this.$refs.chatWindow;
                if (win) win.scrollTop = win.scrollHeight;
            });
        }
    }));
});
