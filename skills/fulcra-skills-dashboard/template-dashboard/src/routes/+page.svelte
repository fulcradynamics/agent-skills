<script>
  import AgentChat from './AgentChat.svelte';
  import D3Timeline from './D3Timeline.svelte';

  const annotations = [];

  // Helper to format timestamps
  function formatTime(isoString) {
    return new Date(isoString).toLocaleString('en-US', {
      month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit'
    });
  }
</script>

<svelte:head>
  <title>Fulcra Dashboard</title>
</svelte:head>

<main class="dashboard-container">
  
  <header>
    <h1>Your Personal Dashboard</h1>
    <p>A canvas for your data.</p>
    <div class="onboarding-banner">
      <p>
        <span class="icon">✨</span>
        <strong>Bring your own data to this dashboard!</strong>
        <br/>
        Download the Context app at <a href="https://fulcradynamics.com/" target="_blank" rel="noopener noreferrer">fulcradynamics.com</a> to sync your local data into the dashboard. 
        Alternatively, you can have your agent feed the dashboard directly by uploading files or creating annotations through the chat!
      </p>
    </div>
  </header>

  <div class="dashboard-grid">
    <!-- Milestone Annotations -->
    <section class="card full-width">
      <h2>Milestone Annotations</h2>
      <D3Timeline data={annotations} title="" color="#4a5568" />
    </section>
  </div>
  
  <AgentChat />
</main>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    background: #f7fafc;
    color: #2d3748;
    font-family: system-ui, -apple-system, sans-serif;
    min-height: 100vh;
    overflow-x: hidden;
  }

  .dashboard-container {
    position: relative;
    max-width: 1000px;
    margin: 0 auto;
    padding: 2rem;
  }

  header {
    text-align: center;
    margin-bottom: 3rem;
  }

  h1 {
    font-size: 3rem;
    color: #1a202c;
    margin: 0 0 0.5rem 0;
  }

  p {
    font-size: 1.2rem;
    color: #4a5568;
    margin: 0;
  }

  .onboarding-banner {
    margin-top: 1.5rem;
    padding: 1rem;
    background: #ebf8ff;
    border: 1px solid #90cdf4;
    border-radius: 8px;
    display: inline-block;
    max-width: 600px;
    text-align: left;
  }

  .onboarding-banner p {
    font-size: 0.95rem;
    color: #2c5282;
    line-height: 1.5;
  }

  .onboarding-banner .icon {
    font-size: 1.2rem;
    margin-right: 0.25rem;
    vertical-align: middle;
  }

  .onboarding-banner strong {
    color: #2b6cb0;
    font-size: 1rem;
  }

  .onboarding-banner a {
    color: #3182ce;
    text-decoration: none;
    border-bottom: 1px dotted #3182ce;
  }

  .onboarding-banner a:hover {
    color: #2b6cb0;
  }

  .dashboard-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 2rem;
  }

  .card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 2rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  }

  h2 {
    margin-top: 0;
    color: #2d3748;
    border-bottom: 1px solid #edf2f7;
    padding-bottom: 0.5rem;
    font-weight: 600;
  }
</style>
