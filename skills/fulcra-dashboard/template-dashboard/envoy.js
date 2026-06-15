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

        async init() {
            if (!isLocal) return; // Do not attempt to fetch on public static hosts
            
            try {
                // Fetch the initial greeting and any history from the Python server
                const response = await fetch('/api/chat');
                if (response.ok) {
                    const result = await response.json();
                    if (result.messages) {
                        this.messages = result.messages;
                        this.scrollToBottom();
                    }
                }
            } catch (err) {
                console.warn('Could not establish connection to local relay.');
            }
        },

        async sendMessage() {
            if (!this.input.trim()) return;

            const userMessage = this.input;
            this.messages.push({ role: 'user', text: userMessage });
            this.input = '';
            
            // Reset textarea height
            if (this.$refs.chatInput) {
                this.$refs.chatInput.style.height = 'auto';
            }
            
            this.isTyping = true;
            this.scrollToBottom();

            try {
                // We POST to our local Python server. 
                // The server will either return a simulated response or route to OpenClaw.
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: userMessage })
                });
                
                if (response.ok) {
                    const result = await response.json();
                    if (result.messages) {
                        this.messages.push(...result.messages);
                    }
                } else {
                    this.messages.push({ role: 'system', text: 'Error: The local relay failed to respond.' });
                }
            } catch (err) {
                this.messages.push({ role: 'system', text: 'Error: Cannot reach the local relay. Ensure the Python server is running.' });
            } finally {
                this.isTyping = false;
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
