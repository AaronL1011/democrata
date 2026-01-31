<script lang="ts">
  interface Column {
    header: string;
    key: string;
    align?: string;
  }

  interface RowData {
    cells?: Record<string, string>;
    [key: string]: string | Record<string, string> | undefined;
  }

  interface Props {
    data: Record<string, unknown>;
  }

  let { data }: Props = $props();

  let title = $derived(data.title as string | undefined);
  let columns = $derived((data.columns as Column[]) || []);
  let rows = $derived((data.rows as RowData[]) || []);
  let caption = $derived(data.caption as string | undefined);

  function getCellValue(row: RowData, key: string): string {
    if (row.cells && typeof row.cells === 'object') {
      return row.cells[key] || '';
    }
    const value = row[key];
    return typeof value === 'string' ? value : '';
  }
</script>

<div class="data-table">
  {#if title}
    <h3 class="title">{title}</h3>
  {/if}

  <div class="table-wrapper">
    <table>
      <thead>
        <tr>
          {#each columns as column}
            <th style:text-align={column.align || 'left'}>{column.header}</th>
          {/each}
        </tr>
      </thead>
      <tbody>
        {#each rows as row}
          <tr>
            {#each columns as column}
              <td style:text-align={column.align || 'left'}>
                {getCellValue(row, column.key)}
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
  .data-table {
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

  th {
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-primary);
    background: var(--color-gray-50);
    text-transform: uppercase;
    font-size: var(--font-size-xs);
    letter-spacing: 0.05em;
  }

  td {
    color: var(--color-gray-600);
  }

  tbody tr {
    transition: background-color var(--transition-fast);
  }

  tbody tr:hover {
    background: var(--color-gray-50);
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
