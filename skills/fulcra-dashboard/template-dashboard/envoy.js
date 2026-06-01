document.addEventListener('alpine:init', () => {
    Alpine.data('chatEnvoy', () => ({
        messages: [{ role: 'assistant', text: 'Telemetry link established. Awaiting command parameters.' }],
        input: '',
        isTyping: false,

        async sendMessage() {
            if (!this.input.trim()) return;

            const userMessage = this.input;
            this.messages.push({ role: 'user', text: userMessage });
            this.input = '';
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
