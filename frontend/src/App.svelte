<script lang="ts">
  import './styles/theme.css';
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
    <p>Non-partisan political data analysis · Factual accuracy without advocacy</p>
  </footer>
</main>
{/if}

<style>
  main {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  header {
    padding: var(--spacing-8);
    text-align: center;
    background: var(--color-surface);
    border-bottom: 1px solid var(--color-border);
    box-shadow: var(--shadow-xs);
  }

  header h1 {
    font-size: var(--font-size-3xl);
    font-weight: var(--font-weight-bold);
    color: var(--color-text-heading);
    margin: 0 0 var(--spacing-2);
    letter-spacing: -0.025em;
  }

  .tagline {
    color: var(--color-text-secondary);
    font-size: var(--font-size-base);
    margin: 0;
  }

  .query-section {
    padding: var(--spacing-8);
    background: var(--color-surface);
    border-bottom: 1px solid var(--color-border);
  }

  .results-section {
    flex: 1;
    padding: var(--spacing-8);
    max-width: var(--max-width-lg);
    width: 100%;
    margin: 0 auto;
  }

  footer {
    padding: var(--spacing-6);
    text-align: center;
    color: var(--color-text-muted);
    font-size: var(--font-size-sm);
    border-top: 1px solid var(--color-border);
    background: var(--color-surface);
  }

  footer p {
    margin: 0;
  }
</style>
