<script>
  // Agents: When you generate custom art for the dashboard, import the file from $lib/assets
  // and inject it below. (e.g., import heroImage from '$lib/assets/my_art.png';)
</script>

<header>
  <h1>Your Personal Dashboard</h1>
  <p>A canvas for your data.</p>
  
  <div class="hero-art" style="display: none;">
      <!-- Inject custom art here: <img src={heroImage} alt="Theme Art" /> -->
  </div>

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

<style>
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

  .hero-art {
    margin: 2rem auto;
    max-width: 800px;
    border-radius: 8px;
    overflow: hidden;
  }

  .hero-art img {
    width: 100%;
    display: block;
  }
</style>