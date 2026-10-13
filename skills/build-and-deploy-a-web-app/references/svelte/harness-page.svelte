<script>
  import { user } from '$lib/user';
  import { onMount } from 'svelte';
  import HarnessDashboard from '$lib/components/HarnessDashboard.svelte';

  onMount(async () => {
    await user.init();
  });
</script>

<svelte:head>
  <title>Harness Dashboard</title>
</svelte:head>

<HarnessDashboard />
