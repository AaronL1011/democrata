<script lang="ts">
  import type { ComponentData } from '$lib/api/client';
  import TextBlock from '$lib/components/ui/TextBlock.svelte';
  import Notice from '$lib/components/ui/Notice.svelte';
  import DataTable from '$lib/components/ui/DataTable.svelte';
  import Chart from '$lib/components/ui/Chart.svelte';
  import Timeline from '$lib/components/ui/Timeline.svelte';
  import Comparison from '$lib/components/ui/Comparison.svelte';
  import MemberProfiles from '$lib/components/ui/MemberProfiles.svelte';
  import VotingBreakdown from '$lib/components/ui/VotingBreakdown.svelte';

  interface Props {
    component: ComponentData;
  }

  let { component }: Props = $props();
</script>

{#if component.type === 'textblock'}
  <TextBlock data={component.data} />
{:else if component.type === 'notice'}
  <Notice data={component.data} />
{:else if component.type === 'datatable'}
  <DataTable data={component.data} />
{:else if component.type === 'chart'}
  <Chart data={component.data} />
{:else if component.type === 'timeline'}
  <Timeline data={component.data} />
{:else if component.type === 'comparison'}
  <Comparison data={component.data} />
{:else if component.type === 'memberprofiles'}
  <MemberProfiles data={component.data} />
{:else if component.type === 'votingbreakdown'}
  <VotingBreakdown data={component.data} />
{:else}
  <div class="unknown">
    <p>Unknown component type: {component.type}</p>
  </div>
{/if}

<style>
  .unknown {
    padding: 1rem;
    background: #f3f4f6;
    border-radius: 0.375rem;
    color: #6b7280;
    font-size: 0.875rem;
  }
</style>
