<script lang="ts">
  import { marked } from 'marked';

  interface Props {
    data: Record<string, unknown>;
  }

  let { data }: Props = $props();

  let title = $derived(data.title as string | undefined);
  let content = $derived(((data.content as string) || '').trim());
  let format = $derived((data.format as string) || 'markdown');

  // marked.parse is sync when async: false (default in browser)
  let renderedContent = $derived.by(() => {
    if (format !== 'markdown') return content;
    return marked.parse(content, { async: false }) as string;
  });
</script>

{#if content}
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
{/if}

<style>
  .text-block {
    line-height: var(--line-height-relaxed);
  }

  .title {
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-primary);
    margin: 0 0 var(--spacing-2);
  }

  .content {
    color: var(--color-gray-700);
  }

  .content :global(p) {
    margin: 0 0 var(--spacing-3);
  }

  .content :global(p:last-child) {
    margin-bottom: 0;
  }

  .content :global(ul),
  .content :global(ol) {
    margin: 0 0 var(--spacing-3) var(--spacing-6);
    padding: 0;
  }

  .content :global(li) {
    margin-bottom: var(--spacing-1);
  }

  .content :global(li:last-child) {
    margin-bottom: 0;
  }

  .content :global(strong) {
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-primary);
  }

  .content :global(a) {
    color: var(--color-primary);
    text-decoration: underline;
    text-underline-offset: 2px;
    transition: color var(--transition-fast);
  }

  .content :global(a:hover) {
    color: var(--color-primary-hover);
  }

  .content :global(code) {
    background: var(--color-gray-100);
    padding: var(--spacing-1) var(--spacing-2);
    border-radius: var(--radius-sm);
    font-size: 0.875em;
    font-family: ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace;
  }

  .content :global(blockquote) {
    margin: var(--spacing-3) 0;
    padding: var(--spacing-3) var(--spacing-4);
    border-left: 3px solid var(--color-primary);
    background: var(--color-gray-50);
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  }

  .content :global(blockquote p:last-child) {
    margin-bottom: 0;
  }
</style>
