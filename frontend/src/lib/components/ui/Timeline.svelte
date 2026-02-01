<script lang="ts">
  interface TimelineEvent {
    date: string;
    label: string;
    description?: string;
    significance?: number;
  }

  interface Props {
    data: Record<string, unknown>;
  }

  let { data }: Props = $props();

  let title = $derived(data.title as string | undefined);
  let events = $derived(
    ((data.events as TimelineEvent[]) || []).filter((e) => e.date || e.label)
  );
  let caption = $derived(data.caption as string | undefined);
</script>

{#if events.length > 0}
  <div class="timeline">
    {#if title}
      <h3 class="title">{title}</h3>
    {/if}

    <div class="events">
      {#each events as event, index}
        <div class="event">
          <div class="marker">
            <div class="dot"></div>
            {#if index < events.length - 1}
              <div class="line"></div>
            {/if}
          </div>
          <div class="content">
            <time class="date">{event.date}</time>
            <h4 class="label">{event.label}</h4>
            {#if event.description}
              <p class="description">{event.description}</p>
            {/if}
          </div>
        </div>
      {/each}
    </div>

    {#if caption}
      <p class="caption">{caption}</p>
    {/if}
  </div>
{/if}

<style>
  .timeline {
    width: 100%;
  }

  .title {
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-primary);
    margin: 0 0 var(--spacing-4);
  }

  .events {
    display: flex;
    flex-direction: column;
  }

  .event {
    display: flex;
    gap: var(--spacing-4);
  }

  .marker {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 1rem;
  }

  .dot {
    width: 0.75rem;
    height: 0.75rem;
    background: var(--color-primary);
    border-radius: var(--radius-full);
    flex-shrink: 0;
    box-shadow: 0 0 0 3px var(--color-primary-muted);
  }

  .line {
    width: 2px;
    flex: 1;
    background: var(--color-border);
    margin: var(--spacing-1) 0;
  }

  .content {
    flex: 1;
    padding-bottom: var(--spacing-6);
  }

  .date {
    font-size: var(--font-size-xs);
    color: var(--color-text-secondary);
    font-weight: var(--font-weight-medium);
    text-transform: uppercase;
    letter-spacing: 0.025em;
  }

  .label {
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-primary);
    margin: var(--spacing-1) 0;
  }

  .description {
    font-size: var(--font-size-sm);
    color: var(--color-gray-600);
    line-height: var(--line-height-normal);
    margin: 0;
  }

  .caption {
    margin: var(--spacing-2) 0 0;
    font-size: var(--font-size-xs);
    color: var(--color-text-secondary);
    font-style: italic;
  }
</style>
