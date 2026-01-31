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

  $effect(() => {
    if (!canvas || series.length === 0) return;

    // Destroy existing chart before creating new one
    chartInstance?.destroy();

    const labels = series[0]?.data.map((d) => d.label) || [];
    const datasets = series.map((s, index) => ({
      label: s.name,
      data: s.data.map((d) => d.value),
      backgroundColor: getColors(index),
      borderColor: getColors(index),
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
          },
        },
        scales:
          chartType !== 'pie' && chartType !== 'doughnut'
            ? {
                x: { title: { display: !!xAxisLabel, text: xAxisLabel || '' } },
                y: { title: { display: !!yAxisLabel, text: yAxisLabel || '' } },
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

  function getColors(index: number): string {
    const colors = [
      '#6366f1',
      '#8b5cf6',
      '#a855f7',
      '#d946ef',
      '#ec4899',
      '#f43f5e',
      '#f97316',
      '#eab308',
    ];
    return colors[index % colors.length];
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
    font-size: 1rem;
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 0.75rem;
  }

  .chart-container {
    height: 300px;
  }

  .caption {
    margin-top: 0.5rem;
    font-size: 0.75rem;
    color: #6b7280;
    font-style: italic;
  }
</style>
