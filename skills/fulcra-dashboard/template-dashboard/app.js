document.addEventListener('alpine:init', () => {
    Alpine.data('dashboard', () => ({
        timelines: [],
        recordsProcessed: [],
        dashboardSummary: '',
        syncDate: new Date().toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }),
        
        async init() {
            try {
                const response = await fetch('data.json?t=' + Date.now());
                const config = await response.json();
                
                this.dashboardSummary = config.summary || 'A high-altitude view of your tracked data.';
                
                const fetchJsonl = async (url) => {
                    if (!url) return [];
                    try {
                        const res = await fetch(url + '?t=' + Date.now());
                        if (!res.ok) return [];
                        const text = await res.text();
                        return text.trim().split('\n').filter(Boolean).map(JSON.parse);
                    } catch (e) {
                        return [];
                    }
                };

                if (config.timelines) {
                    for (let tl of config.timelines) {
                        if (typeof tl.data === 'string' && tl.data.endsWith('.jsonl')) {
                            tl.data = await fetchJsonl(tl.data);
                        }
                    }
                    this.timelines = config.timelines;
                }

                let rawRecords = config.recordsProcessed || [];
                if (typeof rawRecords === 'string' && rawRecords.endsWith('.jsonl')) {
                    rawRecords = await fetchJsonl(rawRecords);
                    const aggregated = {};
                    for (const r of rawRecords) {
                        const type = r.metadata?.name || r.metadata?.data_type || r.annotation_type || r.fulcra_data_type || 'Unknown';
                        const val = typeof r.value === 'number' ? r.value : 1;
                        aggregated[type] = (aggregated[type] || 0) + val;
                    }
                    this.recordsProcessed = Object.entries(aggregated).map(([type, count]) => ({ type, count }));
                } else {
                    this.recordsProcessed = rawRecords;
                }
            } catch (err) {
                console.error("Failed to load dashboard config/data", err);
            }
        }
    }));

    Alpine.data('timelineComponent', (timeline) => ({
        hoverIndex: null,
        parsedData: [],
        
        init() {
            this.parsedData = (timeline.data || []).map(d => ({
                ...d,
                parsedDate: new Date(d.recorded_at || d.time || d.date)
            })).sort((a, b) => a.parsedDate - b.parsedDate);
            
            this.$nextTick(() => {
                if (this.parsedData.length > 0 && this.$refs.chartZone) {
                    drawD3Timeline(this.parsedData, this.$refs.chartZone, timeline.color);
                }
            });
        },
        
        get displayedDetails() {
            if (this.parsedData.length === 0) return [];
            let startIndex = this.hoverIndex !== null ? this.hoverIndex : this.parsedData.length - 1;
            let details = [];
            for (let i = 0; i < 5; i++) {
                let idx = startIndex - i;
                if (idx >= 0 && idx < this.parsedData.length) {
                    details.push({ item: this.parsedData[idx], isHovered: this.hoverIndex === idx });
                }
            }
            return details;
        },
        
        getIcon(d) {
            if (d.type === 'backup' || (d.label && d.label.toLowerCase().includes('backup'))) return '💾';
            if (d.type === 'annotation' || (d.label && d.label.toLowerCase().includes('note'))) return '📝';
            return '⏺️';
        },
        
        getTier(d) {
            if (d.type === 'backup' || (d.label && d.label.toLowerCase().includes('backup'))) return 'Archival';
            if (d.type === 'annotation' || (d.label && d.label.toLowerCase().includes('note'))) return 'Annotation';
            return 'Event';
        },
        
        formatValue(d) {
            if (d.value === undefined || d.value === null) return '';
            
            // Special formatting for ScaleAnnotations
            if (d.metadata && d.metadata.measurement_spec && d.metadata.measurement_spec.measurement_type === 'scale') {
                const maxVal = d.metadata.measurement_spec.scale.max_allowed || 5;
                let textStr = `${d.value}/${maxVal}`;
                
                // Look for a custom label mapping
                if (d.metadata.spec && d.metadata.spec.scale && d.metadata.spec.scale.label_mapping && d.metadata.spec.scale.label_mapping.string && d.metadata.spec.scale.label_mapping.string.mapping) {
                   const label = d.metadata.spec.scale.label_mapping.string.mapping[String(d.value)];
                   if (label) {
                       textStr += ` &mdash; <em>${label}</em>`;
                   }
                }
                return textStr;
            }
            
            // Fallback for primitive values
            return d.value;
        }
    }));

    Alpine.data('barChartComponent', () => ({
        init() {},
        updateChart(data) {
            if (data && data.length > 0 && this.$refs.barChartZone) {
                setTimeout(() => {
                    drawD3BarChart(data, this.$refs.barChartZone);
                }, 50);
            }
        }
    }));
});

// ==========================================
// 🎨 PROVINCE: D3.js VISUALIZATIONS
// ==========================================

function drawD3BarChart(data, container) {
    d3.select(container).selectAll("*").remove();
    const margin = { top: 30, right: 60, bottom: 40, left: 150 };
    const width = container.clientWidth - margin.left - margin.right || 600;
    const height = Math.max(250, data.length * 40);

    const svg = d3.select(container).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    const sortedData = [...data].sort((a, b) => b.count - a.count);

    const x = d3.scaleLinear()
        .domain([0, d3.max(sortedData, d => d.count) * 1.15])
        .range([0, width]);

    svg.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x).ticks(5))
        .attr("color", "#a0aec0")
        .selectAll("text").style("font-family", "inherit").style("fill", "#718096");

    const y = d3.scaleBand()
        .range([0, height])
        .domain(sortedData.map(d => d.type))
        .padding(.1);

    svg.append("g")
        .call(d3.axisLeft(y))
        .attr("color", "#a0aec0")
        .selectAll("text").style("font-family", "inherit").style("fill", "#718096").style("font-size", "12px");

    const colorScale = d3.scaleOrdinal()
        .domain(sortedData.map(d => d.type))
        .range(d3.quantize(t => d3.interpolateBlues(t * 0.8 + 0.2), sortedData.length).reverse());

    svg.selectAll("myRect")
        .data(sortedData).enter().append("rect")
        .attr("x", x(0))
        .attr("y", d => y(d.type))
        .attr("width", d => x(d.count))
        .attr("height", y.bandwidth())
        .attr("fill", d => colorScale(d.type))
        .attr("rx", 4)
        .style("opacity", 0.8)
        .on("mouseover", function() { d3.select(this).style("opacity", 1).attr("stroke", "#fff").attr("stroke-width", 1); })
        .on("mouseout", function() { d3.select(this).style("opacity", 0.8).attr("stroke", "none"); });

    svg.selectAll(".text")
        .data(sortedData).enter().append("text")
        .attr("y", d => y(d.type) + y.bandwidth() / 2 + 4)
        .attr("x", d => x(d.count) + 5)
        .text(d => d.count.toLocaleString())
        .style("fill", "#f0f0f0").style("font-size", "12px").style("font-family", "inherit");
}

function drawD3Timeline(parsedData, container, color) {
    d3.select(container).selectAll("*").remove();
    
    const width = container.clientWidth || 800;
    const height = container.clientHeight || 120;
    const margin = {top: 20, right: 20, bottom: 30, left: 20};
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const svg = d3.select(container).append("svg")
        .attr("width", width)
        .attr("height", height);
        
    const g = svg.append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    const tooltip = d3.select(container).append("div")
        .attr("class", "d3-tooltip")
        .style("opacity", 0);

    if (!parsedData || parsedData.length === 0) return;

    const x = d3.scaleTime()
        .domain(d3.extent(parsedData, d => d.parsedDate))
        .range([0, innerWidth]);

    const y = d3.scaleLinear()
        .domain([0, d3.max(parsedData, d => typeof d.value === 'number' ? d.value : 1)])
        .range([innerHeight, 0]);

    // Add subtle grid lines
    g.append("g")
        .attr("class", "grid")
        .attr("transform", `translate(0,${innerHeight})`)
        .call(d3.axisBottom(x).tickSize(-innerHeight).tickFormat(""))
        .attr("stroke-opacity", 0.1)
        .attr("color", "#a0aec0");

    const hasValues = parsedData.some(d => typeof d.value === 'number');

    if (hasValues && parsedData.length > 1) {
        const line = d3.line()
            .x(d => x(d.parsedDate))
            .y(d => y(d.value))
            .curve(d3.curveMonotoneX);

        g.append("path")
            .datum(parsedData)
            .attr("fill", "none")
            .attr("stroke", color || "var(--chart-line-1)")
            .attr("stroke-width", 2)
            .attr("d", line);
    }

    g.selectAll("circle")
        .data(parsedData)
        .enter().append("circle")
        .attr("cx", d => x(d.parsedDate))
        .attr("cy", d => hasValues ? y(d.value) : innerHeight / 2)
        .attr("r", 5)
        .attr("fill", color || "var(--chart-line-1)")
        .attr("stroke", "var(--bg-dark)")
        .attr("stroke-width", 2)
        .on("mouseover", function(event, d) {
            const idx = parsedData.indexOf(d);
            d3.select(container).node().dispatchEvent(new CustomEvent('timeline-hover', { detail: { index: idx } }));
            
            d3.select(this).attr("r", 8);
            tooltip.transition().duration(200).style("opacity", .9);
            tooltip.html(`Value: ${d.value || 1}<br/>${d.parsedDate.toLocaleDateString()}`)
                .style("left", (event.pageX) + "px")
                .style("top", (event.pageY - 28) + "px");
        })
        .on("mouseout", function() {
            d3.select(container).node().dispatchEvent(new CustomEvent('timeline-hover', { detail: { index: null } }));
            
            d3.select(this).attr("r", 5);
            tooltip.transition().duration(500).style("opacity", 0);
        });

    g.append("g")
        .attr("transform", `translate(0,${innerHeight})`)
        .call(d3.axisBottom(x).ticks(5))
        .attr("color", "#a0aec0")
        .selectAll("text").style("font-family", "inherit");
}

// ---------------------------------------------------------
// 🚀 ADVANCED CHART EXAMPLES (Agent Toolkit)
// Agents: Use these as references when the user requests 
// exotic visualizations like heatmaps, donuts, or radar charts.
// ---------------------------------------------------------

/**
 * Renders a D3 Donut Chart
 * Useful for displaying categorical proportions.
 */
function drawD3DonutChart(data, container, valueKey = "count", labelKey = "type") {
    d3.select(container).selectAll("*").remove();
    const width = container.clientWidth || 300;
    const height = container.clientHeight || 300;
    const margin = 20;
    const radius = Math.min(width, height) / 2 - margin;

    const svg = d3.select(container).append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", `translate(${width / 2},${height / 2})`);

    const color = d3.scaleOrdinal()
        .domain(data.map(d => d[labelKey]))
        .range(d3.schemeDark2);

    const pie = d3.pie().value(d => d[valueKey])(data);
    const arc = d3.arc().innerRadius(radius * 0.5).outerRadius(radius);

    svg.selectAll("path")
        .data(pie)
        .enter()
        .append("path")
        .attr("d", arc)
        .attr("fill", d => color(d.data[labelKey]))
        .attr("stroke", "rgba(0,0,0,0.2)")
        .style("stroke-width", "2px")
        .style("opacity", 0.8)
        .on("mouseover", function() { d3.select(this).style("opacity", 1); })
        .on("mouseout", function() { d3.select(this).style("opacity", 0.8); });
}

/**
 * Renders a D3 Calendar Heatmap
 * Useful for visualizing daily frequency or intensity over time.
 */
function drawD3CalendarHeatmap(data, container, dateKey = "parsedDate", valueKey = "value") {
    d3.select(container).selectAll("*").remove();
    
    // Simple implementation aggregating by day of week vs week of year
    const width = container.clientWidth || 600;
    const cellSize = 15;
    const height = cellSize * 7 + 40;

    const svg = d3.select(container).append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", `translate(40, 20)`);

    const timeWeek = d3.timeSunday;
    const timeDay = d3.timeDay;

    const color = d3.scaleSequential(d3.interpolateGreens)
        .domain([0, d3.max(data, d => d[valueKey] || 1)]);

    svg.selectAll("rect")
        .data(data)
        .enter().append("rect")
        .attr("width", cellSize - 1)
        .attr("height", cellSize - 1)
        .attr("x", d => timeWeek.count(d3.timeYear(d[dateKey]), d[dateKey]) * cellSize)
        .attr("y", d => d[dateKey].getDay() * cellSize)
        .attr("fill", d => color(d[valueKey] || 1))
        .attr("rx", 2)
        .append("title")
        .text(d => `${d[dateKey].toLocaleDateString()}: ${d[valueKey] || 1}`);
}

/**
 * Renders a D3 Radar Chart
 * Useful for displaying multivariate data (e.g. multiple metrics for a specific day or category).
 */
function drawD3RadarChart(data, container, features) {
    d3.select(container).selectAll("*").remove();
    
    // Expects data format: [{ name: "Category A", values: { feature1: 10, feature2: 20 } }, ...]
    const width = container.clientWidth || 400;
    const height = container.clientHeight || 400;
    const margin = 50;
    const radius = Math.min(width, height) / 2 - margin;
    
    const svg = d3.select(container).append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", `translate(${width/2},${height/2})`);
        
    const angleSlice = Math.PI * 2 / features.length;
    
    // Draw concentric circles
    const levels = 5;
    for(let i=0; i<levels; i++) {
        const levelFactor = radius * ((i+1)/levels);
        svg.append("circle")
            .attr("r", levelFactor)
            .style("fill", "none")
            .style("stroke", "rgba(0,0,0,0.1)")
            .style("stroke-dasharray", "4,4");
    }
    
    // Draw axis lines and labels
    const axis = svg.selectAll(".axis")
        .data(features)
        .enter()
        .append("g")
        .attr("class", "axis");
        
    axis.append("line")
        .attr("x1", 0).attr("y1", 0)
        .attr("x2", (d, i) => radius * Math.cos(angleSlice * i - Math.PI/2))
        .attr("y2", (d, i) => radius * Math.sin(angleSlice * i - Math.PI/2))
        .style("stroke", "rgba(0,0,0,0.2)")
        .style("stroke-width", "1px");
        
    axis.append("text")
        .attr("class", "legend")
        .style("font-size", "11px")
        .attr("text-anchor", "middle")
        .attr("dy", "0.35em")
        .attr("x", (d, i) => (radius + 20) * Math.cos(angleSlice * i - Math.PI/2))
        .attr("y", (d, i) => (radius + 20) * Math.sin(angleSlice * i - Math.PI/2))
        .text(d => d);
        
    // Draw radar polygons
    const color = d3.scaleOrdinal(d3.schemeSet2);
    
    // Scale function
    const maxValue = d3.max(data, d => d3.max(features, f => d.values[f] || 0));
    const rScale = d3.scaleLinear().range([0, radius]).domain([0, maxValue || 1]);
    
    const radarLine = d3.lineRadial()
        .angle((d, i) => i * angleSlice)
        .radius(d => rScale(d.value))
        .curve(d3.curveLinearClosed);
        
    const polygons = svg.selectAll(".radar-wrapper")
        .data(data)
        .enter().append("g");
        
    polygons.append("path")
        .attr("class", "radar-area")
        .attr("d", d => {
            const mappedValues = features.map(f => ({ axis: f, value: d.values[f] || 0 }));
            return radarLine(mappedValues);
        })
        .style("fill", (d, i) => color(i))
        .style("fill-opacity", 0.4)
        .style("stroke", (d, i) => color(i))
        .style("stroke-width", "2px")
        .on("mouseover", function() {
            d3.selectAll(".radar-area").style("fill-opacity", 0.1);
            d3.select(this).style("fill-opacity", 0.7);
        })
        .on("mouseout", function() {
            d3.selectAll(".radar-area").style("fill-opacity", 0.4);
        });
}

/**
 * Renders an Interactive, Rotatable 3D Scatter Plot using Plotly.js
 * Agent note: If you use this, you must inject the Plotly CDN into index.html:
 * <script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
 * 
 * Useful for finding clusters or outliers across 3 distinct dimensions (e.g. Time vs. Amount vs. Frequency).
 */
function drawPlotly3DScatter(data, container, xKey = "x", yKey = "y", zKey = "z", labelKey = "label") {
    // Ensure container is a DOM node
    const domNode = typeof container === 'string' ? document.getElementById(container) : container;
    if (!domNode) return;
    
    domNode.innerHTML = ""; // Clear any existing D3 or Plotly charts
    
    if (typeof Plotly === 'undefined') {
        console.error("Plotly is not loaded. Please add the CDN script to index.html.");
        domNode.innerHTML = "<p style='color:var(--text-muted); text-align:center; padding:2rem;'>Plotly.js missing. Add CDN to index.html.</p>";
        return;
    }

    const trace = {
        x: data.map(d => d[xKey]),
        y: data.map(d => d[yKey]),
        z: data.map(d => d[zKey]),
        text: data.map(d => d[labelKey] || ''),
        mode: 'markers',
        marker: {
            size: 6,
            color: data.map(d => d[zKey]), // Color gradient by Z axis
            colorscale: 'Viridis',
            opacity: 0.8,
            line: { width: 0.5, color: 'rgba(255,255,255,0.3)' }
        },
        type: 'scatter3d',
        hovertemplate: `${xKey}: %{x}<br>${yKey}: %{y}<br>${zKey}: %{z}<br><b>%{text}</b><extra></extra>`
    };

    const layout = {
        margin: { l: 0, r: 0, b: 0, t: 0 },
        paper_bgcolor: 'rgba(0,0,0,0)', // Transparent to match dashboard themes
        plot_bgcolor: 'rgba(0,0,0,0)',
        scene: {
            xaxis: { title: xKey, showbackground: false, gridcolor: "rgba(128,128,128,0.2)", zerolinecolor: "rgba(128,128,128,0.5)" },
            yaxis: { title: yKey, showbackground: false, gridcolor: "rgba(128,128,128,0.2)", zerolinecolor: "rgba(128,128,128,0.5)" },
            zaxis: { title: zKey, showbackground: false, gridcolor: "rgba(128,128,128,0.2)", zerolinecolor: "rgba(128,128,128,0.5)" },
            camera: {
                eye: { x: 1.5, y: 1.5, z: 1.2 } // Initial rotation angle
            }
        }
    };

    const config = {
        responsive: true,
        displayModeBar: false // Keep it clean for the dashboard UI
    };

    Plotly.newPlot(domNode, [trace], layout, config);
}
