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
  let events = $derived((data.events as TimelineEvent[]) || []);
  let caption = $derived(data.caption as string | undefined);
</script>

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

<style>
  .timeline {
    width: 100%;
  }

  .title {
    font-size: 1rem;
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 1rem;
  }

  .events {
    display: flex;
    flex-direction: column;
  }

  .event {
    display: flex;
    gap: 1rem;
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
    background: #6366f1;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .line {
    width: 2px;
    flex: 1;
    background: #e5e7eb;
    margin: 0.25rem 0;
  }

  .content {
    flex: 1;
    padding-bottom: 1.5rem;
  }

  .date {
    font-size: 0.75rem;
    color: #6b7280;
    font-weight: 500;
  }

  .label {
    font-size: 0.875rem;
    font-weight: 600;
    color: #1f2937;
    margin: 0.25rem 0;
  }

  .description {
    font-size: 0.875rem;
    color: #4b5563;
    line-height: 1.5;
  }

  .caption {
    margin-top: 0.5rem;
    font-size: 0.75rem;
    color: #6b7280;
    font-style: italic;
  }
</style>
