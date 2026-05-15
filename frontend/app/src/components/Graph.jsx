import { useEffect, useRef, useState, useCallback } from "react";
import * as d3 from "d3";

const CLUSTER_COLORS = [
    "#8b5cf6",
    "#06b6d4",
    "#f59e0b",
    "#ef4444",
    "#10b981",
    "#ec4899",
    "#3b82f6",
    "#f97316",
];

/**
 * Compute node radius based on summary length.
 * @param {string} summary
 * @returns {number} radius between 6 and 14
 */
function nodeRadius(summary) {
    const len = (summary || "").length;
    return Math.min(14, Math.max(6, 6 + (len / 500) * 8));
}

/**
 * Generate intra-cluster links.
 * For clusters with <= 5 nodes, fully connect.
 * For larger clusters, connect each node to its 2-3 nearest neighbors.
 * @param {Array} nodes
 * @returns {Array} links
 */
function generateIntraClusterLinks(nodes) {
    const clusters = new Map();
    for (const node of nodes) {
        if (!clusters.has(node.cluster)) clusters.set(node.cluster, []);
        clusters.get(node.cluster).push(node);
    }

    const links = [];
    for (const [, members] of clusters) {
        if (members.length <= 5) {
            for (let i = 0; i < members.length; i++) {
                for (let j = i + 1; j < members.length; j++) {
                    links.push({ source: members[i].id, target: members[j].id });
                }
            }
        } else {
            const added = new Set();
            for (let i = 0; i < members.length; i++) {
                const others = members
                    .map((m, idx) => ({ idx, dist: Math.abs(i - idx) }))
                    .filter((o) => o.idx !== i)
                    .sort((a, b) => a.dist - b.dist)
                    .slice(0, 3);
                for (const o of others) {
                    const key = [Math.min(i, o.idx), Math.max(i, o.idx)].join("-");
                    if (!added.has(key)) {
                        added.add(key);
                        links.push({
                            source: members[i].id,
                            target: members[o.idx].id,
                        });
                    }
                }
            }
        }
    }
    return links;
}

/**
 * Expand a convex hull outward by a given padding.
 * @param {Array} hull - array of [x, y] points
 * @param {number} padding
 * @returns {Array} expanded hull points
 */
function expandHull(hull, padding) {
    const centroid = d3.polygonCentroid(hull);
    return hull.map(([x, y]) => {
        const dx = x - centroid[0];
        const dy = y - centroid[1];
        const len = Math.sqrt(dx * dx + dy * dy) || 1;
        return [x + (dx / len) * padding, y + (dy / len) * padding];
    });
}

/**
 * Standalone, reusable D3 force-directed graph component.
 * @param {{ nodes: Array, links: Array, onNodeClick: Function }} props
 */
const Graph = ({ nodes, links, onNodeClick }) => {
    const containerRef = useRef(null);
    const svgRef = useRef(null);
    const simulationRef = useRef(null);
    const [tooltip, setTooltip] = useState(null);
    const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

    const clusterCount = new Set(nodes.map((n) => n.cluster)).size;
    const svgLabel = `Force-directed cluster graph of ${nodes.length} Wikipedia ${
        nodes.length === 1 ? "article" : "articles"
    } in ${clusterCount} ${clusterCount === 1 ? "cluster" : "clusters"}`;

    // Track dimensions with ResizeObserver
    useEffect(() => {
        const container = containerRef.current;
        if (!container) return;

        const ro = new ResizeObserver((entries) => {
            const { width, height } = entries[0].contentRect;
            if (width > 0 && height > 0) {
                setDimensions({ width, height });
            }
        });
        ro.observe(container);
        return () => ro.disconnect();
    }, []);

    const handleNodeClick = useCallback(
        (event, d) => {
            if (onNodeClick) onNodeClick(d);
        },
        [onNodeClick],
    );

    // Main D3 render
    useEffect(() => {
        if (!nodes.length) return;

        const svg = d3.select(svgRef.current);
        svg.selectAll("*").remove();

        const { width, height } = dimensions;
        svg.attr("viewBox", [0, 0, width, height]);

        // Screen-reader title and description as first SVG children.
        svg.append("title").text(svgLabel);
        svg.append("desc").text(
            "Each circle represents a Wikipedia article; circles are coloured and grouped by cluster. Use the Tab key to focus a node, then press Enter or Space to open its details panel.",
        );

        const clusterIds = [...new Set(nodes.map((n) => n.cluster))];
        const color = d3
            .scaleOrdinal()
            .domain(clusterIds)
            .range(CLUSTER_COLORS);

        // Zoom behavior
        const zoomGroup = svg.append("g");
        const zoomBehavior = d3
            .zoom()
            .scaleExtent([0.3, 5])
            .on("zoom", (event) => {
                zoomGroup.attr("transform", event.transform);
            });
        svg.call(zoomBehavior);

        // Layers in order: hulls, links, nodes
        const hullGroup = zoomGroup.append("g").attr("class", "hulls");
        const linkGroup = zoomGroup.append("g").attr("class", "links");
        const nodeGroup = zoomGroup.append("g").attr("class", "nodes");

        // Build simulation-compatible node copies
        const simNodes = nodes.map((n) => ({
            ...n,
            radius: nodeRadius(n.summary),
        }));
        const simLinks = links.map((l) => ({ ...l }));

        // Force simulation
        const simulation = d3
            .forceSimulation(simNodes)
            .force(
                "link",
                d3
                    .forceLink(simLinks)
                    .id((d) => d.id)
                    .distance(80),
            )
            .force("charge", d3.forceManyBody().strength(-200))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force(
                "collide",
                d3.forceCollide().radius((d) => d.radius + 2),
            );

        simulationRef.current = simulation;

        // Links
        const linkSel = linkGroup
            .selectAll("line")
            .data(simLinks)
            .join("line")
            .attr("stroke", "#ffffff")
            .attr("stroke-opacity", 0.08)
            .attr("stroke-width", 1);

        // Nodes
        const nodeSel = nodeGroup
            .selectAll("circle")
            .data(simNodes)
            .join("circle")
            .attr("r", 0)
            .attr("fill", (d) => color(d.cluster))
            .attr("stroke", (d) => d3.color(color(d.cluster)).brighter(0.6))
            .attr("stroke-width", 1.5)
            .attr("cursor", "pointer")
            .attr("opacity", 0)
            .attr("tabindex", 0)
            .attr("role", "button")
            .attr(
                "aria-label",
                (d) => `Article ${d.id}, cluster ${d.cluster}. Press Enter to view details.`,
            )
            .on("focus", (event, d) => {
                const rect = containerRef.current.getBoundingClientRect();
                const circle = event.currentTarget.getBoundingClientRect();
                setTooltip({
                    x: circle.left - rect.left + circle.width + 4,
                    y: circle.top - rect.top - 8,
                    title: d.id,
                    summary: (d.summary || "").slice(0, 180),
                    color: color(d.cluster),
                });
                d3.select(event.currentTarget)
                    .attr("r", d.radius * 1.4)
                    .attr("stroke-width", 3);
            })
            .on("blur", (event, d) => {
                setTooltip(null);
                d3.select(event.currentTarget)
                    .attr("r", d.radius)
                    .attr("stroke-width", 1.5);
            })
            .on("keydown", (event, d) => {
                if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    if (onNodeClick) onNodeClick(d);
                }
            })
            .on("mouseover", (event, d) => {
                const rect = containerRef.current.getBoundingClientRect();
                setTooltip({
                    x: event.clientX - rect.left + 12,
                    y: event.clientY - rect.top - 8,
                    title: d.id,
                    summary: (d.summary || "").slice(0, 180),
                    color: color(d.cluster),
                });
                d3.select(event.currentTarget)
                    .transition()
                    .duration(150)
                    .attr("r", d.radius * 1.4)
                    .attr("stroke-width", 3);
            })
            .on("mousemove", (event) => {
                const rect = containerRef.current.getBoundingClientRect();
                setTooltip((prev) =>
                    prev
                        ? {
                              ...prev,
                              x: event.clientX - rect.left + 12,
                              y: event.clientY - rect.top - 8,
                          }
                        : null,
                );
            })
            .on("mouseout", (event, d) => {
                setTooltip(null);
                d3.select(event.currentTarget)
                    .transition()
                    .duration(150)
                    .attr("r", d.radius)
                    .attr("stroke-width", 1.5);
            })
            .on("click", handleNodeClick);

        // Entry animation with staggered delay
        nodeSel
            .transition()
            .delay((_, i) => i * 40)
            .duration(500)
            .ease(d3.easeCubicOut)
            .attr("r", (d) => d.radius)
            .attr("opacity", 1);

        // Drag behavior
        const drag = d3
            .drag()
            .on("start", (event, d) => {
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            })
            .on("drag", (event, d) => {
                d.fx = event.x;
                d.fy = event.y;
            })
            .on("end", (event, d) => {
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            });
        nodeSel.call(drag);

        // Cluster hulls — updated every tick
        function updateHulls() {
            const hullData = [];
            for (const cid of clusterIds) {
                const points = simNodes
                    .filter((n) => n.cluster === cid)
                    .map((n) => [n.x, n.y]);
                if (points.length >= 3) {
                    const hull = d3.polygonHull(points);
                    if (hull) {
                        hullData.push({ cluster: cid, path: hull });
                    }
                }
            }

            hullGroup
                .selectAll("path")
                .data(hullData, (d) => d.cluster)
                .join("path")
                .attr("d", (d) => {
                    const expanded = expandHull(d.path, 18);
                    return `M${expanded.join("L")}Z`;
                })
                .attr("fill", (d) => color(d.cluster))
                .attr("fill-opacity", 0.1)
                .attr("stroke", (d) => color(d.cluster))
                .attr("stroke-opacity", 0.2)
                .attr("stroke-width", 1);
        }

        // Simulation tick handler
        simulation.on("tick", () => {
            linkSel
                .attr("x1", (d) => d.source.x)
                .attr("y1", (d) => d.source.y)
                .attr("x2", (d) => d.target.x)
                .attr("y2", (d) => d.target.y);

            nodeSel.attr("cx", (d) => d.x).attr("cy", (d) => d.y);

            updateHulls();
        });

        return () => {
            simulation.stop();
        };
    }, [nodes, links, dimensions, handleNodeClick, onNodeClick, svgLabel]);

    return (
        <div ref={containerRef} className="relative w-full h-full">
            <svg
                ref={svgRef}
                className="w-full h-full"
                style={{ display: "block" }}
                role="img"
                aria-label={svgLabel}
            />
            {tooltip && (
                <div
                    className="pointer-events-none absolute z-50 max-w-xs rounded-lg border px-3 py-2 text-sm shadow-lg"
                    style={{
                        left: tooltip.x,
                        top: tooltip.y,
                        backgroundColor: "#292929",
                        borderColor: tooltip.color,
                        color: "#d4d4d4",
                    }}
                >
                    <div
                        className="mb-1 font-semibold"
                        style={{ color: tooltip.color }}
                    >
                        {tooltip.title}
                    </div>
                    {tooltip.summary && (
                        <div className="text-xs leading-relaxed opacity-80">
                            {tooltip.summary}
                            {tooltip.summary.length >= 180 ? "..." : ""}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export { generateIntraClusterLinks, nodeRadius };
export default Graph;
