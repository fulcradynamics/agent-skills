<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';

  // The raw data points to visualize
  let { data = [], title = "Data Breakdown", color = "#64c466" } = $props();

  /** @type {HTMLElement} */
  let container;

  // Aggregate data by type
  let aggregatedData = $derived.by(() => {
    if (!data || data.length === 0) return [];
    
    const counts = {};
    data.forEach(d => {
      // Handle the nested structure of RecordsProcessed
      const type = d.record?.type || d.type || 'Unknown';
      counts[type] = (counts[type] || 0) + 1;
    });

    return Object.entries(counts)
      .map(([type, count]) => ({ type, count }))
      .sort((a, b) => b.count - a.count);
  });

  onMount(() => {
    if (!aggregatedData || aggregatedData.length === 0) return;

    const margin = { top: 30, right: 30, bottom: 40, left: 100 };
    const width = container.clientWidth - margin.left - margin.right;
    const height = Math.max(200, aggregatedData.length * 40);

    // Clear previous SVG
    d3.select(container).selectAll("*").remove();

    const svg = d3.select(container)
      .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // X axis (Count)
    const x = d3.scaleLinear()
      .domain([0, d3.max(aggregatedData, d => d.count)])
      .range([0, width]);

    svg.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(x).ticks(5))
      .attr("color", "rgba(255,255,255,0.5)")
      .selectAll("text")
      .style("font-family", "inherit")
      .style("fill", "rgba(255,255,255,0.8)");

    // Y axis (Type)
    const y = d3.scaleBand()
      .range([0, height])
      .domain(aggregatedData.map(d => d.type))
      .padding(.1);

    svg.append("g")
      .call(d3.axisLeft(y))
      .attr("color", "rgba(255,255,255,0.5)")
      .selectAll("text")
      .style("font-family", "inherit")
      .style("fill", "rgba(255,255,255,0.8)")
      .style("font-size", "12px");

    // Color scale
    const colorScale = d3.scaleOrdinal()
      .domain(aggregatedData.map(d => d.type))
      .range(d3.quantize(t => d3.interpolateGreens(t * 0.8 + 0.2), aggregatedData.length).reverse());

    // Bars
    svg.selectAll("myRect")
      .data(aggregatedData)
      .enter()
      .append("rect")
      .attr("x", x(0) )
      .attr("y", d => y(d.type))
      .attr("width", d => x(d.count))
      .attr("height", y.bandwidth())
      .attr("fill", d => colorScale(d.type))
      .attr("rx", 4)
      .style("opacity", 0.8)
      .on("mouseover", function() {
        d3.select(this).style("opacity", 1).attr("stroke", "#fff").attr("stroke-width", 1);
      })
      .on("mouseout", function() {
        d3.select(this).style("opacity", 0.8).attr("stroke", "none");
      });

    // Value Labels
    svg.selectAll(".text")
      .data(aggregatedData)
      .enter()
      .append("text")
      .attr("class", "label")
      .attr("y", d => y(d.type) + y.bandwidth() / 2 + 4)
      .attr("x", d => x(d.count) + 5)
      .text(d => d.count.toLocaleString())
      .style("fill", "rgba(255,255,255,0.9)")
      .style("font-size", "12px")
      .style("font-family", "inherit");
  });
</script>

<div class="chart-wrapper">
  <h4>{title}</h4>
  <div class="chart-container" bind:this={container}></div>
</div>

<style>
  .chart-wrapper {
    margin: 1rem 0;
    padding: 1rem;
    background: rgba(0, 0, 0, 0.2);
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.1);
  }

  h4 {
    margin: 0 0 1rem 0;
    color: rgba(255,255,255,0.9);
    font-weight: normal;
    font-size: 1.1rem;
  }

  .chart-container {
    width: 100%;
    min-height: 200px;
    overflow: visible;
  }
</style>
