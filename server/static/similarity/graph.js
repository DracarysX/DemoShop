// Product Similarity Graph using D3.js
function createSimilarityGraph(nodes, edges) {
    const width = document.getElementById('graph').parentElement.clientWidth - 60;
    const height = 700;
    
    const svg = d3.select("#graph")
        .attr("width", width)
        .attr("height", height);
    
    // Clear any existing content
    svg.selectAll("*").remove();
    
    // Create force simulation with increased spacing
    const simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(edges)
            .id(d => d.id)
            .distance(d => 350 * (1 - d.similarity * 0.3))) // Much larger distance
        .force("charge", d3.forceManyBody().strength(-800)) // Stronger repulsion
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("collision", d3.forceCollide().radius(60)); // Larger collision radius
    
    // Create arrow markers for directed edges (optional)
    svg.append("defs").selectAll("marker")
        .data(["end"])
        .join("marker")
        .attr("id", String)
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 20)
        .attr("refY", 0)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("path")
        .attr("fill", "#94a3b8")
        .attr("d", "M0,-5L10,0L0,5");
    
    // Create edges (lines)
    const link = svg.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(edges)
        .join("line")
        .attr("class", "edge-line")
        .attr("stroke", d => {
            // Professional color gradient from blue to green
            const hue = 200 + (d.similarity * 60); // 200 (blue) to 260 (cyan-green)
            return `hsl(${hue}, 70%, 50%)`;
        })
        .attr("stroke-width", d => 2 + (d.similarity * 6))
        .attr("stroke-opacity", 0.6);
    
    // Create edge labels (similarity scores)
    const edgeLabels = svg.append("g")
        .attr("class", "edge-labels")
        .selectAll("text")
        .data(edges)
        .join("text")
        .attr("class", "edge-label")
        .text(d => `${(d.similarity * 100).toFixed(0)}%`)
        .attr("font-size", 11)
        .attr("font-weight", 600)
        .attr("fill", "#64748b")
        .attr("text-anchor", "middle");
    
    // Create nodes (circles)
    const node = svg.append("g")
        .attr("class", "nodes")
        .selectAll("circle")
        .data(nodes)
        .join("circle")
        .attr("class", "node-circle")
        .attr("r", d => 15 + Math.sqrt(d.engagement) * 3)
        .attr("fill", "#3b82f6")
        .attr("stroke", "#fff")
        .attr("stroke-width", 3)
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));
    
    // Add node labels
    const label = svg.append("g")
        .attr("class", "labels")
        .selectAll("text")
        .data(nodes)
        .join("text")
        .attr("class", "node-label")
        .text(d => d.name)
        .attr("font-size", 13)
        .attr("font-weight", 600)
        .attr("fill", "#0f172a")
        .attr("text-anchor", "middle")
        .attr("dy", -25);
    
    // Add tooltips
    node.append("title")
        .text(d => `${d.name}\nEngagement: ${d.engagement.toFixed(1)}`);
    
    link.append("title")
        .text(d => `Similarity: ${(d.similarity * 100).toFixed(1)}%`);
    
    // Update positions on each tick
    simulation.on("tick", () => {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);
        
        edgeLabels
            .attr("x", d => (d.source.x + d.target.x) / 2)
            .attr("y", d => (d.source.y + d.target.y) / 2);
        
        node
            .attr("cx", d => d.x)
            .attr("cy", d => d.y);
        
        label
            .attr("x", d => d.x)
            .attr("y", d => d.y);
    });
    
    // Drag functions
    function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
    }
    
    function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
    }
    
    function dragended(event) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
    }
    
    // Add zoom functionality
    const zoom = d3.zoom()
        .scaleExtent([0.5, 3])
        .on("zoom", (event) => {
            svg.selectAll("g").attr("transform", event.transform);
        });
    
    svg.call(zoom);
    
    return simulation;
}

// Update similarity threshold dynamically
function updateThreshold(threshold) {
    document.getElementById('thresholdValue').textContent = threshold + '%';
    // Reload page with new threshold
    const url = new URL(window.location);
    url.searchParams.set('threshold', threshold / 100);
    window.location.href = url.toString();
}

