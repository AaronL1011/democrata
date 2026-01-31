<script lang="ts">
  interface ComparisonItem {
    name: string;
    description?: string;
  }

  interface ComparisonAttribute {
    name: string;
    values: string[];
  }

  interface Props {
    data: Record<string, unknown>;
  }

  let { data }: Props = $props();

  let title = $derived(data.title as string | undefined);
  let items = $derived((data.items as ComparisonItem[]) || []);
  let attributes = $derived((data.attributes as ComparisonAttribute[]) || []);
  let caption = $derived(data.caption as string | undefined);
</script>

<div class="comparison">
  {#if title}
    <h3 class="title">{title}</h3>
  {/if}

  <div class="table-wrapper">
    <table>
      <thead>
        <tr>
          <th class="attribute-header"></th>
          {#each items as item}
            <th class="item-header">
              <span class="item-name">{item.name}</span>
              {#if item.description}
                <span class="item-description">{item.description}</span>
              {/if}
            </th>
          {/each}
        </tr>
      </thead>
      <tbody>
        {#each attributes as attribute}
          <tr>
            <td class="attribute-name">{attribute.name}</td>
            {#each attribute.values as value, i}
              <td class="attribute-value" class:first={i === 0} class:last={i === items.length - 1}>
                {value}
              </td>
            {/each}
          </tr>
        {/each}
      </tbody>
    </table>
  </div>

  {#if caption}
    <p class="caption">{caption}</p>
  {/if}
</div>

<style>
  .comparison {
    width: 100%;
  }

  .title {
    font-size: 1rem;
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 0.75rem;
  }

  .table-wrapper {
    overflow-x: auto;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.875rem;
  }

  th,
  td {
    padding: 0.75rem 1rem;
    border-bottom: 1px solid #e5e7eb;
  }

  .attribute-header {
    width: 30%;
  }

  .item-header {
    text-align: center;
    background: #f9fafb;
    vertical-align: top;
  }

  .item-name {
    display: block;
    font-weight: 600;
    color: #1f2937;
  }

  .item-description {
    display: block;
    font-size: 0.75rem;
    font-weight: 400;
    color: #6b7280;
    margin-top: 0.25rem;
  }

  .attribute-name {
    font-weight: 500;
    color: #374151;
    background: #f9fafb;
  }

  .attribute-value {
    text-align: center;
    color: #4b5563;
  }

  .attribute-value.first {
    background: #eff6ff;
  }

  .attribute-value.last {
    background: #fef2f2;
  }

  tbody tr:hover td {
    background: #f3f4f6;
  }

  tbody tr:hover .attribute-value.first {
    background: #dbeafe;
  }

  tbody tr:hover .attribute-value.last {
    background: #fee2e2;
  }

  .caption {
    margin-top: 0.5rem;
    font-size: 0.75rem;
    color: #6b7280;
    font-style: italic;
  }
</style>
