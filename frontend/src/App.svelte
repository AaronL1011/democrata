<script lang="ts">
  import QueryInput from '$lib/components/query/QueryInput.svelte';
  import QueryResults from '$lib/components/query/QueryResults.svelte';
  import UploadPage from '$lib/components/upload/UploadPage.svelte';

  let currentPath = $state(window.location.pathname);

  $effect(() => {
    const handlePopState = () => {
      currentPath = window.location.pathname;
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  });
</script>

{#if currentPath === '/upload'}
  <UploadPage />
{:else}
<main>
  <header>
    <h1>Polly Pipeline</h1>
    <p class="tagline">
      Understand political information through clear, factual analysis
    </p>
  </header>

  <section class="query-section">
    <QueryInput />
  </section>

  <section class="results-section">
    <QueryResults />
  </section>

  <footer>
    <p>Non-partisan political data analysis • Factual accuracy without advocacy</p>
  </footer>
</main>
{/if}

<style>
  :global(body) {
    margin: 0;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
      sans-serif;
    background: #f9fafb;
    color: #1f2937;
    line-height: 1.5;
  }

  :global(*) {
    box-sizing: border-box;
  }

  main {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  header {
    padding: 2rem;
    text-align: center;
    background: white;
    border-bottom: 1px solid #e5e7eb;
  }

  header h1 {
    font-size: 1.75rem;
    font-weight: 700;
    color: #111827;
    margin: 0 0 0.5rem;
  }

  .tagline {
    color: #6b7280;
    margin: 0;
  }

  .query-section {
    padding: 2rem;
    background: white;
    border-bottom: 1px solid #e5e7eb;
  }

  .results-section {
    flex: 1;
    padding: 2rem;
    max-width: 64rem;
    width: 100%;
    margin: 0 auto;
  }

  footer {
    padding: 1.5rem;
    text-align: center;
    color: #9ca3af;
    font-size: 0.875rem;
    border-top: 1px solid #e5e7eb;
    background: white;
  }

  footer p {
    margin: 0;
  }
</style>
