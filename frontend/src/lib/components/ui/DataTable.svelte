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

  th {
    font-weight: 600;
    color: #374151;
    background: #f9fafb;
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.05em;
  }

  td {
    color: #4b5563;
  }

  tbody tr:hover {
    background: #f9fafb;
  }

  .caption {
    margin-top: 0.5rem;
    font-size: 0.75rem;
    color: #6b7280;
    font-style: italic;
  }
</style>
