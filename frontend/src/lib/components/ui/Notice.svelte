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
    padding: var(--spacing-4);
    border-radius: var(--radius-md);
    border-left: 4px solid;
  }

  .info {
    background: var(--color-primary-light);
    border-color: var(--color-primary);
  }

  .warning {
    background: var(--color-warning-light);
    border-color: var(--color-warning);
  }

  .important {
    background: var(--color-error-light);
    border-color: var(--color-error);
  }

  .title {
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-semibold);
    margin: 0 0 var(--spacing-1);
  }

  .info .title {
    color: var(--color-primary-active);
  }

  .warning .title {
    color: var(--color-warning-text);
  }

  .important .title {
    color: var(--color-error-text);
  }

  .message {
    font-size: var(--font-size-sm);
    line-height: var(--line-height-normal);
    margin: 0;
  }

  .info .message {
    color: var(--color-primary-active);
  }

  .warning .message {
    color: var(--color-warning-text);
  }

  .important .message {
    color: var(--color-error-text);
  }
</style>
