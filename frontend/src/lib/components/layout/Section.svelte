<script lang="ts">
  import type { ComponentData, SectionLayout, ComponentSize } from '$lib/api/client';
  import ComponentRenderer from './ComponentRenderer.svelte';

  interface Props {
    title?: string;
    components: ComponentData[];
    layout?: SectionLayout;
  }

  let { title, components, layout }: Props = $props();

  // Component types that should always be full width
  const FULL_WIDTH_TYPES = new Set(['datatable', 'comparison', 'timeline', 'textblock']);
  
  // Component types that CAN be half-width when paired
  const PAIRABLE_TYPES = new Set(['chart', 'votingbreakdown', 'notice', 'memberprofiles']);

  // Determine the effective size for a component
  function getComponentSize(component: ComponentData, useGrid: boolean): ComponentSize {
    // Explicit size from backend takes precedence
    if (component.size) return component.size;
    
    // In stack layout, everything is full width
    if (!useGrid) return 'full';
    
    // Auto-determine based on type
    if (FULL_WIDTH_TYPES.has(component.type)) return 'full';
    if (PAIRABLE_TYPES.has(component.type)) return 'half';
    
    return 'full';
  }

  // Determine the best layout for this section
  function determineLayout(): SectionLayout {
    // Explicit layout from backend takes precedence
    if (layout) return layout;
    
    // Single component = always stack
    if (components.length <= 1) return 'stack';
    
    // Count pairable components (charts, voting breakdowns, etc.)
    const pairableComponents = components.filter(c => 
      PAIRABLE_TYPES.has(c.type) || c.size === 'half'
    );
    
    // Only use grid if we have EXACTLY 2 pairable components
    // This creates intentional side-by-side pairings
    if (pairableComponents.length === 2 && components.length === 2) {
      return 'grid';
    }
    
    // For mixed content, default to stack for cleaner reading
    return 'stack';
  }

  let effectiveLayout = $derived(determineLayout());

  // Get CSS class for component size
  function getSizeClass(component: ComponentData): string {
    const size = getComponentSize(component, effectiveLayout !== 'stack');
    
    switch (size) {
      case 'full': return 'size-full';
      case 'half': return 'size-half';
      case 'third': return 'size-third';
      case 'two-thirds': return 'size-two-thirds';
      default: return 'size-full';
    }
  }
</script>

<section class="section">
  {#if title}
    <h2 class="section-title">{title}</h2>
  {/if}

  <div class="components layout-{effectiveLayout}">
    {#each components as component (component.id)}
      <div class="component-wrapper {getSizeClass(component)}">
        <ComponentRenderer {component} />
      </div>
    {/each}
  </div>
</section>

<style>
  .section {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: var(--spacing-6);
    box-shadow: var(--shadow-sm);
  }

  .section-title {
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-primary);
    margin: 0 0 var(--spacing-5);
    padding-bottom: var(--spacing-3);
    border-bottom: 1px solid var(--color-border-light);
  }

  /* Stack Layout (single column - default) */
  .components.layout-stack {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-5);
  }

  /* Grid Layout (two-column for paired components) */
  .components.layout-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-5);
  }

  /* Two Column Layout */
  .components.layout-two-column {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-5);
  }

  /* Three Column Layout */
  .components.layout-three-column {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--spacing-5);
  }

  /* Component Size Classes */
  .component-wrapper {
    min-width: 0;
  }

  .layout-grid .size-full,
  .layout-two-column .size-full,
  .layout-three-column .size-full {
    grid-column: 1 / -1;
  }

  .layout-three-column .size-two-thirds {
    grid-column: span 2;
  }

  .layout-grid .size-half,
  .layout-two-column .size-half {
    grid-column: span 1;
  }

  .layout-three-column .size-third {
    grid-column: span 1;
  }

  /* Responsive: stack on smaller screens */
  @media (max-width: 900px) {
    .components.layout-grid,
    .components.layout-two-column,
    .components.layout-three-column {
      grid-template-columns: 1fr;
    }

    .size-full,
    .size-half,
    .size-third,
    .size-two-thirds {
      grid-column: 1 / -1;
    }
  }
</style>
