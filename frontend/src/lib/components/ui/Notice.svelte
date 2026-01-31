<script lang="ts">
  interface Props {
    data: Record<string, unknown>;
  }

  let { data }: Props = $props();

  let title = $derived(data.title as string | undefined);
  let message = $derived(data.message as string || '');
  let level = $derived((data.level as string) || 'info');

  let levelClass = $derived(
    level === 'warning' ? 'warning' : level === 'important' ? 'important' : 'info'
  );
</script>

<div class="notice {levelClass}">
  {#if title}
    <h4 class="title">{title}</h4>
  {/if}
  <p class="message">{message}</p>
</div>

<style>
  .notice {
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid;
  }

  .info {
    background: #eff6ff;
    border-color: #3b82f6;
  }

  .warning {
    background: #fffbeb;
    border-color: #f59e0b;
  }

  .important {
    background: #fef2f2;
    border-color: #ef4444;
  }

  .title {
    font-size: 0.875rem;
    font-weight: 600;
    margin-bottom: 0.25rem;
  }

  .info .title {
    color: #1e40af;
  }

  .warning .title {
    color: #b45309;
  }

  .important .title {
    color: #b91c1c;
  }

  .message {
    font-size: 0.875rem;
    line-height: 1.5;
  }

  .info .message {
    color: #1e40af;
  }

  .warning .message {
    color: #92400e;
  }

  .important .message {
    color: #991b1b;
  }
</style>
