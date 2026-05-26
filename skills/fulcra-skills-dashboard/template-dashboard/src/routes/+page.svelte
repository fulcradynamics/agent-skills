<script>
  import AgentChat from './AgentChat.svelte';
  import ThemeStyles from './ThemeStyles.svelte';
  import HeroHeader from './HeroHeader.svelte';
  import DashboardGrid from './DashboardGrid.svelte';

  // Core Data Stores (Populate these via the agent data ingestion step)
  const annotations = [];

</script>

<svelte:head>
  <title>Fulcra Dashboard</title>
</svelte:head>

<ThemeStyles />

<main class="dashboard-container">
  
  <HeroHeader />

  <DashboardGrid {annotations} />
  
  <AgentChat />

</main>