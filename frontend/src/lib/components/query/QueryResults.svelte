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
      <span>•</span>
      <span>{$queryStore.response.metadata.processing_time_ms}ms</span>
      {#if $queryStore.response.cached}
        <span>•</span>
        <span class="cached">Cached</span>
      {/if}
    </div>
  {/if}
{/if}

<style>
  .error {
    padding: 1rem;
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 0.5rem;
    color: #991b1b;
    margin-top: 1rem;
  }

  .loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    padding: 3rem;
    color: #6b7280;
  }

  .spinner {
    width: 2rem;
    height: 2rem;
    border: 3px solid #e5e7eb;
    border-top-color: #3b82f6;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  .metadata {
    display: flex;
    gap: 0.5rem;
    justify-content: center;
    margin-top: 1.5rem;
    font-size: 0.875rem;
    color: #6b7280;
  }

  .cached {
    color: #059669;
    font-weight: 500;
  }
</style>
