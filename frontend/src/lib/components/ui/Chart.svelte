<script lang="ts">
  import { Chart, registerables } from 'chart.js';

  Chart.register(...registerables);

  interface ChartSeries {
    name: string;
    data: Array<{ label: string; value: number }>;
  }

  interface Props {
    data: Record<string, unknown>;
  }

  let { data }: Props = $props();

  let title = $derived(data.title as string | undefined);
  let chartType = $derived((data.chart_type as string) || 'bar');
  let series = $derived((data.series as ChartSeries[]) || []);
  let xAxisLabel = $derived(data.x_axis_label as string | undefined);
  let yAxisLabel = $derived(data.y_axis_label as string | undefined);
  let caption = $derived(data.caption as string | undefined);

  let canvas: HTMLCanvasElement | undefined = $state();
  let chartInstance: Chart | null = null;

  const CHART_COLORS = [
    '#6366f1', // indigo
    '#8b5cf6', // violet
    '#ec4899', // pink
    '#f43f5e', // rose
    '#f97316', // orange
    '#eab308', // yellow
    '#22c55e', // green
    '#14b8a6', // teal
  ];

  $effect(() => {
    if (!canvas || series.length === 0) return;

    chartInstance?.destroy();

    const labels = series[0]?.data.map((d) => d.label) || [];
    const datasets = series.map((s, index) => ({
      label: s.name,
      data: s.data.map((d) => d.value),
      backgroundColor: CHART_COLORS[index % CHART_COLORS.length],
      borderColor: CHART_COLORS[index % CHART_COLORS.length],
      borderWidth: 1,
    }));

    chartInstance = new Chart(canvas, {
      type: mapChartType(chartType),
      data: { labels, datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: series.length > 1,
            labels: {
              font: {
                family: 'system-ui, -apple-system, sans-serif',
              },
            },
          },
        },
        scales:
          chartType !== 'pie' && chartType !== 'doughnut'
            ? {
                x: {
                  title: { display: !!xAxisLabel, text: xAxisLabel || '' },
                  grid: { color: 'rgba(0, 0, 0, 0.05)' },
                },
                y: {
                  title: { display: !!yAxisLabel, text: yAxisLabel || '' },
                  grid: { color: 'rgba(0, 0, 0, 0.05)' },
                },
              }
            : undefined,
      },
    });

    return () => {
      chartInstance?.destroy();
    };
  });

  function mapChartType(type: string): 'bar' | 'line' | 'pie' | 'doughnut' {
    const typeMap: Record<string, 'bar' | 'line' | 'pie' | 'doughnut'> = {
      bar: 'bar',
      horizontal_bar: 'bar',
      stacked_bar: 'bar',
      line: 'line',
      pie: 'pie',
      doughnut: 'doughnut',
    };
    return typeMap[type] || 'bar';
  }
</script>

<div class="chart">
  {#if title}
    <h3 class="title">{title}</h3>
  {/if}

  <div class="chart-container">
    <canvas bind:this={canvas}></canvas>
  </div>

  {#if caption}
    <p class="caption">{caption}</p>
  {/if}
</div>

<style>
  .chart {
    width: 100%;
  }

  .title {
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-primary);
    margin: 0 0 var(--spacing-3);
  }

  .chart-container {
    height: 300px;
    padding: var(--spacing-2);
    background: var(--color-surface);
    border-radius: var(--radius-md);
  }

  .caption {
    margin: var(--spacing-2) 0 0;
    font-size: var(--font-size-xs);
    color: var(--color-text-secondary);
    font-style: italic;
  }
</style>
