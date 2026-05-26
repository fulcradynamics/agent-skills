<script>
  import D3Timeline from './D3Timeline.svelte';

  // These are the baseline props passed from +page.svelte
  let { annotations = [] } = $props();
</script>

<div class="dashboard-grid">
  <!-- Milestone Annotations -->
  <section class="card full-width">
    <h2>Milestone Annotations</h2>
    <D3Timeline data={annotations} title="" color="#4a5568" />
  </section>
</div>

<style>
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