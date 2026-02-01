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
  let items = $derived(
    ((data.items as ComparisonItem[]) || []).filter((i) => i.name)
  );
  let attributes = $derived(
    ((data.attributes as ComparisonAttribute[]) || []).filter(
      (a) => a.name && a.values && a.values.length > 0
    )
  );
  let caption = $derived(data.caption as string | undefined);
  let hasData = $derived(items.length > 0 && attributes.length > 0);
</script>

{#if hasData}
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
{/if}

<style>
  .comparison {
    width: 100%;
  }

  .title {
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-primary);
    margin: 0 0 var(--spacing-3);
  }

  .table-wrapper {
    overflow-x: auto;
    border-radius: var(--radius-md);
    border: 1px solid var(--color-border);
  }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: var(--font-size-sm);
  }

  th,
  td {
    padding: var(--spacing-3) var(--spacing-4);
    border-bottom: 1px solid var(--color-border-light);
  }

  .attribute-header {
    width: 30%;
  }

  .item-header {
    text-align: center;
    background: var(--color-gray-50);
    vertical-align: top;
  }

  .item-name {
    display: block;
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-primary);
  }

  .item-description {
    display: block;
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-normal);
    color: var(--color-text-secondary);
    margin-top: var(--spacing-1);
  }

  .attribute-name {
    font-weight: var(--font-weight-medium);
    color: var(--color-gray-700);
    background: var(--color-gray-50);
  }

  .attribute-value {
    text-align: center;
    color: var(--color-gray-600);
  }

  .attribute-value.first {
    background: var(--color-primary-light);
  }

  .attribute-value.last {
    background: var(--color-error-light);
  }

  tbody tr {
    transition: background-color var(--transition-fast);
  }

  tbody tr:hover td {
    background: var(--color-gray-100);
  }

  tbody tr:hover .attribute-value.first {
    background: var(--color-primary-muted);
  }

  tbody tr:hover .attribute-value.last {
    background: var(--color-error-muted);
  }

  tbody tr:last-child td {
    border-bottom: none;
  }

  .caption {
    margin: var(--spacing-2) 0 0;
    font-size: var(--font-size-xs);
    color: var(--color-text-secondary);
    font-style: italic;
  }
</style>
