<script lang="ts">
  import type { ComponentData } from '$lib/api/client';
  import ComponentRenderer from './ComponentRenderer.svelte';

  interface Props {
    title?: string;
    components: ComponentData[];
  }

  let { title, components }: Props = $props();
</script>

<section class="section">
  {#if title}
    <h2 class="section-title">{title}</h2>
  {/if}

  <div class="components">
    {#each components as component (component.id)}
      <ComponentRenderer {component} />
    {/each}
  </div>
</section>

<style>
  .section {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    padding: 1.5rem;
  }

  .section-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: #374151;
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #e5e7eb;
  }

  .components {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
</style>
