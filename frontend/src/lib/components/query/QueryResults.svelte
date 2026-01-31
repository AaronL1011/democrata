<script lang="ts">
  import { queryStore, layout, components } from '$lib/stores/query';
  import Dashboard from '$lib/components/layout/Dashboard.svelte';
</script>

{#if $queryStore.error}
  <div class="error">
    <p>{$queryStore.error}</p>
  </div>
{:else if $queryStore.isLoading}
  <div class="loading">
    <div class="spinner"></div>
    <p>Searching documents and generating response...</p>
  </div>
{:else if $layout && $components.length > 0}
  <Dashboard layout={$layout} components={$components} />
  
  {#if $queryStore.response}
    <div class="metadata">
      <span>Retrieved {$queryStore.response.metadata.documents_retrieved} documents</span>
      <span class="separator">·</span>
      <span>{$queryStore.response.metadata.processing_time_ms / 1000}s</span>
      {#if $queryStore.response.cached}
        <span class="separator">·</span>
        <span class="cached">Cached</span>
      {/if}
    </div>
  {/if}
{/if}

<style>
  .error {
    padding: var(--spacing-4);
    background: var(--color-error-light);
    border: 1px solid var(--color-error-muted);
    border-radius: var(--radius-md);
    color: var(--color-error-text);
    margin-top: var(--spacing-4);
  }

  .error p {
    margin: 0;
    font-size: var(--font-size-sm);
    line-height: var(--line-height-normal);
  }

  .loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-4);
    padding: var(--spacing-12);
    color: var(--color-text-secondary);
  }

  .loading p {
    margin: 0;
    font-size: var(--font-size-sm);
  }

  .spinner {
    width: 2rem;
    height: 2rem;
    border: 3px solid var(--color-border);
    border-top-color: var(--color-primary);
    border-radius: var(--radius-full);
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  .metadata {
    display: flex;
    gap: var(--spacing-2);
    justify-content: center;
    align-items: center;
    margin-top: var(--spacing-6);
    font-size: var(--font-size-sm);
    color: var(--color-text-secondary);
  }

  .separator {
    color: var(--color-text-muted);
  }

  .cached {
    color: var(--color-success);
    font-weight: var(--font-weight-medium);
  }
</style>
