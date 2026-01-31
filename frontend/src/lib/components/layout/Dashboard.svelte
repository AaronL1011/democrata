<script lang="ts">
  import type { LayoutData, ComponentData } from '$lib/api/client';
  import Section from './Section.svelte';

  interface Props {
    layout: LayoutData;
    components: ComponentData[];
  }

  let { layout, components }: Props = $props();

  function getComponentsForSection(componentIds: string[]): ComponentData[] {
    return componentIds
      .map((id) => components.find((c) => c.id === id))
      .filter((c): c is ComponentData => c !== undefined);
  }
</script>

<div class="dashboard">
  {#if layout.title}
    <h1 class="title">{layout.title}</h1>
  {/if}
  
  {#if layout.subtitle}
    <p class="subtitle">{layout.subtitle}</p>
  {/if}

  <div class="sections">
    {#each layout.sections as section}
      <Section
        title={section.title}
        components={getComponentsForSection(section.component_ids)}
      />
    {/each}
  </div>
</div>

<style>
  .dashboard {
    margin-top: 2rem;
  }

  .title {
    font-size: 1.5rem;
    font-weight: 600;
    color: #111827;
    margin-bottom: 0.5rem;
  }

  .subtitle {
    font-size: 1rem;
    color: #6b7280;
    margin-bottom: 1.5rem;
  }

  .sections {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }
</style>
