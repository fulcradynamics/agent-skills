<script>
  // This is a drop-in Svelte component for the Fulcra Agent Chat UI.
  // Agents: When adding this to the dashboard, inject it at the bottom of +page.svelte
  // or as a persistent overlay.

  import { onMount } from 'svelte';

  let messages = $state([]);
  let input = $state('');
  let isTyping = $state(false);
  let chatWindow = $state();

  async function fetchMessages() {
    try {
      const res = await fetch('/api/chat');
      if (res.ok) {
        messages = await res.json();
        if (messages.length > 0) {
            isTyping = messages[messages.length - 1].role === 'user';
        }
      }
    } catch (err) {
      console.error('Failed to fetch messages', err);
    }
  }

  onMount(() => {
    fetchMessages();
    const interval = setInterval(fetchMessages, 3000);
    return () => clearInterval(interval);
  });

  // Quick suggestions for other POC skills
  const suggestedSkills = [
    { id: "fulcra-calendar-vitals", name: "Calendar Vitals", icon: "📅" },
    { id: "fulcra-location-vitals", name: "Location Vitals", icon: "🗺️" },
    { id: "fulcra-media-vitals", name: "Media Vitals", icon: "🎵" },
    { id: "fulcra-otter-vitals", name: "Otter Vitals", icon: "🎙️" }
  ];

  function sendSuggestion(skillId) {
    input = `Tell me about the ${skillId} skill and help me set it up.`;
    sendMessage();
  }

  async function sendMessage() {
    if (!input.trim()) return;

    const userMessage = input;
    messages = [...messages, { role: 'user', text: userMessage }];
    input = '';
    isTyping = true;

    try {
      isTyping = true;
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: userMessage })
      });

      if (!response.ok) throw new Error('Failed to save message.');
      
      await fetchMessages(); // Fetch updated list
    } catch (error) {
      messages = [...messages, { role: 'system', text: 'Error: The message could not be saved.' }];
      isTyping = false;
    }
  }

  function handleKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  $effect(() => {
    // This effect automatically scrolls the chat window when messages change
    if (chatWindow && messages) {
      chatWindow.scrollTop = chatWindow.scrollHeight;
    }
  });
</script>

<div class="agent-chat-container">
  <div class="chat-header">
    <h3>Agent Comms</h3>
    <div class="status-indicator" class:active={!isTyping} class:typing={isTyping}></div>
  </div>

  <div class="suggestions-panel">
    <div class="suggestions-title">Available Skills</div>
    <div class="suggestions-grid">
      {#each suggestedSkills as skill}
        <button class="suggestion-btn" on:click={() => sendSuggestion(skill.id)}>
          <span class="skill-icon">{skill.icon}</span>
          <span class="skill-name">{skill.name}</span>
        </button>
      {/each}
    </div>
  </div>

  <div class="chat-window" bind:this={chatWindow}>
    {#each messages as msg}
      <div class="message {msg.role}">
        <div class="bubble">{msg.text}</div>
      </div>
    {/each}
    {#if isTyping}
      <div class="message assistant typing-indicator">
        <div class="bubble">...</div>
      </div>
    {/if}
  </div>

  <div class="chat-input">
    <textarea 
      bind:value={input} 
      on:keydown={handleKeydown}
      placeholder="Ask the agent to build something new..."
      rows="2"
    ></textarea>
    <button on:click={sendMessage} disabled={isTyping || !input.trim()}>Send</button>
  </div>
</div>

<style>
  /* 
    Agents: These styles are modular but should be adapted to fit the user's chosen theme!
    For example, in a Cyberpunk theme, change borders to #ff00ff and backgrounds to #0a0a0a. 
  */
  .agent-chat-container {
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    width: 350px;
    background: rgba(20, 40, 30, 0.9);
    border: 2px solid #5a7d65;
    border-radius: 12px;
    display: flex;
    flex-direction: column;
    box-shadow: 0 8px 32px rgba(0,0,0,0.6);
    backdrop-filter: blur(8px);
    z-index: 100;
    overflow: hidden;
  }

  .chat-header {
    background: rgba(0,0,0,0.4);
    padding: 0.75rem 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #5a7d65;
  }

  .chat-header h3 {
    margin: 0;
    font-size: 1rem;
    color: #c4d9c6;
    font-weight: normal;
  }

  .status-indicator {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #666;
  }

  .status-indicator.active { background: #64c466; box-shadow: 0 0 8px #64c466; }
  .status-indicator.typing { background: #e0b441; box-shadow: 0 0 8px #e0b441; animation: pulse 1s infinite; }

  @keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }

  .suggestions-panel {
    padding: 0.75rem 1rem;
    background: rgba(0,0,0,0.2);
    border-bottom: 1px solid #5a7d65;
  }

  .suggestions-title {
    font-size: 0.8rem;
    color: #8ba888;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.5rem;
  }

  .suggestions-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem;
  }

  .suggestion-btn {
    background: rgba(255,255,255,0.05);
    border: 1px solid #5a7d65;
    border-radius: 6px;
    padding: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #c4d9c6;
    font-size: 0.85rem;
    cursor: pointer;
    transition: background 0.2s, transform 0.1s;
    text-align: left;
  }

  .suggestion-btn:hover {
    background: rgba(255,255,255,0.1);
    transform: translateY(-1px);
  }

  .chat-window {
    height: 300px;
    overflow-y: auto;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .message {
    display: flex;
    max-width: 85%;
  }

  .message.user { align-self: flex-end; }
  .message.assistant { align-self: flex-start; }
  .message.system { align-self: center; max-width: 100%; font-size: 0.8rem; color: #ff6b6b; font-style: italic; }

  .bubble {
    padding: 0.6rem 0.8rem;
    border-radius: 8px;
    font-size: 0.95rem;
    line-height: 1.4;
  }

  .user .bubble {
    background: #3b887a;
    color: #fff;
    border-bottom-right-radius: 0;
  }

  .assistant .bubble {
    background: rgba(255,255,255,0.1);
    color: #e4efe7;
    border-bottom-left-radius: 0;
  }

  .typing-indicator .bubble {
    font-weight: bold;
    letter-spacing: 2px;
  }

  .chat-input {
    display: flex;
    gap: 0.5rem;
    padding: 1rem;
    background: rgba(0,0,0,0.3);
    border-top: 1px solid #5a7d65;
  }

  textarea {
    flex: 1;
    background: rgba(255,255,255,0.05);
    border: 1px solid #729676;
    border-radius: 6px;
    padding: 0.5rem;
    color: #fff;
    font-family: inherit;
    resize: none;
    outline: none;
  }

  textarea:focus { border-color: #64c466; }

  button {
    background: #3b887a;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 0 1rem;
    cursor: pointer;
    font-weight: bold;
    transition: background 0.2s;
  }

  button:hover:not(:disabled) { background: #4a9e8f; }
  button:disabled { background: #555; cursor: not-allowed; color: #888; }
</style>
