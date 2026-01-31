<script lang="ts">
  import { marked } from 'marked';

  interface Props {
    data: Record<string, unknown>;
  }

  let { data }: Props = $props();

  let title = $derived(data.title as string | undefined);
  let content = $derived((data.content as string) || '');
  let format = $derived((data.format as string) || 'markdown');

  // marked.parse is sync when async: false (default in browser)
  let renderedContent = $derived.by(() => {
    if (format !== 'markdown') return content;
    return marked.parse(content, { async: false }) as string;
  });
</script>

<div class="text-block">
  {#if title}
    <h3 class="title">{title}</h3>
  {/if}
  <div class="content">
    {#if format === 'markdown'}
      {@html renderedContent}
    {:else}
      <p>{content}</p>
    {/if}
  </div>
</div>

<style>
  .text-block {
    line-height: 1.6;
  }

  .title {
    font-size: 1rem;
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 0.5rem;
  }

  .content :global(p) {
    margin-bottom: 0.75rem;
  }

  .content :global(p:last-child) {
    margin-bottom: 0;
  }

  .content :global(ul),
  .content :global(ol) {
    margin-left: 1.5rem;
    margin-bottom: 0.75rem;
  }

  .content :global(li) {
    margin-bottom: 0.25rem;
  }

  .content :global(strong) {
    font-weight: 600;
  }

  .content :global(a) {
    color: #2563eb;
    text-decoration: underline;
  }

  .content :global(code) {
    background: #f3f4f6;
    padding: 0.125rem 0.375rem;
    border-radius: 0.25rem;
    font-size: 0.875em;
  }
</style>
