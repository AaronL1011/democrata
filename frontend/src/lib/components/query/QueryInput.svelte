<script lang="ts">
  import { queryStore } from '$lib/stores/query';

  let query = $state('');

  async function handleSubmit(e: Event) {
    e.preventDefault();
    if (!query.trim() || $queryStore.isLoading) return;
    await queryStore.execute(query.trim());
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      handleSubmit(e);
    }
  }
</script>

<form onsubmit={handleSubmit} class="query-form">
  <div class="input-wrapper">
    <textarea
      bind:value={query}
      onkeydown={handleKeydown}
      placeholder="Ask a question about politics, legislation, or government..."
      disabled={$queryStore.isLoading}
      rows="2"
    ></textarea>
    <button type="submit" disabled={!query.trim() || $queryStore.isLoading}>
      {$queryStore.isLoading ? 'Searching...' : 'Search'}
    </button>
  </div>
</form>

<style>
  .query-form {
    width: 100%;
    max-width: 48rem;
    margin: 0 auto;
  }

  .input-wrapper {
    display: flex;
    gap: 0.75rem;
    align-items: flex-end;
  }

  textarea {
    flex: 1;
    padding: 0.75rem 1rem;
    font-size: 1rem;
    border: 1px solid #d1d5db;
    border-radius: 0.5rem;
    resize: none;
    font-family: inherit;
  }

  textarea:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  textarea:disabled {
    background: #f9fafb;
  }

  button {
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
    font-weight: 500;
    background: #1f2937;
    color: white;
    border: none;
    border-radius: 0.5rem;
    cursor: pointer;
    white-space: nowrap;
  }

  button:hover:not(:disabled) {
    background: #374151;
  }

  button:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }
</style>
