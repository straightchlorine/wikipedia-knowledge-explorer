import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import * as d3 from "d3";
import LoadingDots from "../common/LoadingDots";
import ErrorTag from "../common/ErrorTag";
import "./Visualize.css";

const API_BASE_URL =
    process.env.REACT_APP_API_BASE_URL || "http://localhost:8000";

const Graph = ({ nodes, links }) => {
    const svgRef = useRef();

    useEffect(() => {
        const svg = d3.select(svgRef.current);
        svg.selectAll("*").remove();

        const width = 600;
        const height = 400;

        svg.attr("viewBox", [0, 0, width, height]);

        const clusterSet = new Set(nodes.map((node) => node.cluster));
        const color = d3
            .scaleOrdinal()
            .domain(clusterSet)
            .range(d3.schemeCategory10);

        const simulation = d3
            .forceSimulation(nodes)
            .force(
                "link",
                d3
                    .forceLink(links)
                    .id((d) => d.id)
                    .distance(100),
            )
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2));

        const link = svg
            .append("g")
            .attr("stroke", "#aaa")
            .selectAll("line")
            .data(links)
            .join("line");

        const node = svg
            .append("g")
            .attr("stroke", "#fff")
            .attr("stroke-width", 1.5)
            .selectAll("circle")
            .data(nodes)
            .join("circle")
            .attr("r", 8)
            .attr("fill", (d) => color(d.cluster))
            .call(drag(simulation));

        const label = svg
            .append("g")
            .selectAll("text")
            .data(nodes)
            .join("text")
            .text((d) => d.id)
            .attr("font-size", 12)
            .attr("fill", "white")
            .attr("dx", 12)
            .attr("dy", "0.35em");

        const legend = svg.append("g").attr("transform", "translate(20, 20)");

        clusterSet.forEach((cluster, i) => {
            const legendRow = legend
                .append("g")
                .attr("transform", `translate(0, ${i * 20})`);

            legendRow
                .append("rect")
                .attr("width", 12)
                .attr("height", 12)
                .attr("fill", color(cluster));

            legendRow
                .append("text")
                .attr("x", 20)
                .attr("y", 10)
                .text(`Cluster ${cluster}`)
                .attr("fill", "white")
                .attr("font-size", "12px");
        });

        node.append("title").text((d) => d.id);

        simulation.on("tick", () => {
            link
                .attr("x1", (d) => d.source.x)
                .attr("y1", (d) => d.source.y)
                .attr("x2", (d) => d.target.x)
                .attr("y2", (d) => d.target.y);

            node.attr("cx", (d) => d.x).attr("cy", (d) => d.y);

            label.attr("x", (d) => d.x).attr("y", (d) => d.y);
        });

        function drag(sim) {
            return d3
                .drag()
                .on("start", (event, d) => {
                    if (!event.active) sim.alphaTarget(0.3).restart();
                    d.fx = d.x;
                    d.fy = d.y;
                })
                .on("drag", (event, d) => {
                    d.fx = event.x;
                    d.fy = event.y;
                })
                .on("end", (event, d) => {
                    if (!event.active) sim.alphaTarget(0);
                    d.fx = null;
                    d.fy = null;
                });
        }
    }, [nodes, links]);

    return <svg ref={svgRef} width="100%" height="400px" />;
};

export const GetLinks = (data) => {
    let links = [];
    let currentClusterIndex = data.articles[0].cluster;
    let previousClusterItems = [];
    let currentClusterItems = [];
    for (const item of data.articles) {
        if (item.cluster !== currentClusterIndex) {
            currentClusterIndex = item.cluster;
            for (const source of previousClusterItems) {
                for (const target of currentClusterItems) {
                    links.push({ source: source, target: target });
                }
            }
            previousClusterItems = currentClusterItems;
            currentClusterItems = [];
        }
        currentClusterItems.push(item.title);
    }
    for (const target of currentClusterItems) {
        for (const source of previousClusterItems) {
            links.push({ source: source, target: target });
        }
    }

    return links;
};

export const GraphComponent = ({ query, resultCount }) => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch(
                    `${API_BASE_URL}/articles/clusters/?query=${encodeURIComponent(query)}&max_results=${resultCount}`,
                );
                if (!response.ok) throw new Error("Failed to fetch data");
                const result = await response.json();
                setData(result);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [query]);

    if (loading) return <LoadingDots />;
    if (error) return <ErrorTag error={error} />;

    data.articles.sort((a, b) => a.cluster - b.cluster);

    const nodes = data.articles.map((item) => ({
        id: item.title,
        cluster: item.cluster,
    }));
    const links = GetLinks(data);

    return <Graph nodes={nodes} links={links} />;
};

const Visualize = () => {
    const [searchParams] = useSearchParams();
    const query = searchParams.get("query");
    const resultCount = searchParams.get("max_results");

    return (
        <>
            <h1 className="center-h1">Visualization of phrase: {query}</h1>
            <GraphComponent query={query} resultCount={resultCount} />
        </>
    );
};

export default Visualize;
