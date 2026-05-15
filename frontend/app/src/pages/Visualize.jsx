import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { X, ExternalLink } from "lucide-react";
import Graph, { generateIntraClusterLinks } from "../components/Graph";
import { apiFetch } from "../lib/api";

/** Pulsing skeleton placeholder for loading state */
function LoadingSkeleton() {
  return (
    <div
      className="flex-1 flex items-center justify-center"
      role="status"
      aria-live="polite"
      aria-label="Clustering articles"
    >
      <div className="flex flex-col items-center gap-4">
        <div className="relative" aria-hidden="true">
          <div
            className="w-32 h-32 rounded-full animate-pulse"
            style={{ backgroundColor: "#3e3e42" }}
          />
          <div
            className="absolute inset-4 rounded-full animate-pulse"
            style={{
              backgroundColor: "#252526",
              animationDelay: "150ms",
            }}
          />
          <div
            className="absolute inset-8 rounded-full animate-pulse"
            style={{
              backgroundColor: "#3e3e42",
              animationDelay: "300ms",
            }}
          />
        </div>
        <p className="text-sm animate-pulse" style={{ color: "#71717a" }}>
          Clustering articles...
        </p>
      </div>
    </div>
  );
}

/** Detail sidebar for a selected article */
function DetailSidebar({ article, onClose }) {
  if (!article) return null;

  const wikiUrl =
    Number.isSafeInteger(article.pageid) && article.pageid > 0
      ? `https://en.wikipedia.org/?curid=${article.pageid}`
      : null;

  return (
    <aside
      className="w-80 shrink-0 flex flex-col overflow-y-auto border-l"
      role="complementary"
      aria-labelledby="article-detail-heading"
      style={{
        backgroundColor: "#252526",
        borderColor: "#3e3e42",
      }}
    >
      <div className="flex items-center justify-between p-4 border-b" style={{ borderColor: "#3e3e42" }}>
        <h2
          id="article-detail-heading"
          className="text-sm font-semibold truncate pr-2"
          style={{ color: "#e4e4e7" }}
        >
          {article.title}
        </h2>
        <button
          onClick={onClose}
          className="p-1 rounded hover:bg-white/10 transition-colors shrink-0"
          style={{ color: "#a1a1aa" }}
          aria-label="Close detail panel"
        >
          <X size={16} aria-hidden="true" />
        </button>
      </div>

      <div className="p-4 flex flex-col gap-4">
        <div>
          <span
            className="inline-block text-xs font-medium px-2 py-0.5 rounded-full"
            style={{
              backgroundColor: "#3e3e42",
              color: "#a1a1aa",
            }}
          >
            Cluster {article.cluster}
          </span>
        </div>

        {article.summary && (
          <p className="text-sm leading-relaxed" style={{ color: "#d4d4d4" }}>
            {article.summary}
          </p>
        )}

        {wikiUrl && (
          <a
            href={wikiUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-sm font-medium transition-colors hover:underline"
            style={{ color: "#8b5cf6" }}
          >
            <ExternalLink size={14} aria-hidden="true" />
            Read on Wikipedia
            <span className="sr-only">(opens in new tab)</span>
          </a>
        )}
      </div>
    </aside>
  );
}

const Visualize = () => {
  const [searchParams] = useSearchParams();
  const query = searchParams.get("query");
  const resultCount = searchParams.get("max_results");

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedArticle, setSelectedArticle] = useState(null);

  useEffect(() => {
    if (!query) return;

    let cancelled = false;
    setLoading(true);
    setError(null);

    const fetchData = async () => {
      try {
        const path = `/api/articles/clusters/?query=${encodeURIComponent(query)}&max_results=${resultCount}`;
        const response = await apiFetch(path);
        if (!response.ok) throw new Error("Failed to fetch cluster data");
        const result = await response.json();
        if (!cancelled) setData(result);
      } catch (err) {
        if (!cancelled) setError(err.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetchData();
    return () => {
      cancelled = true;
    };
  }, [query, resultCount]);

  // Build nodes and links from data
  let nodes = [];
  let links = [];
  if (data && data.articles) {
    const sorted = [...data.articles].sort((a, b) => a.cluster - b.cluster);
    nodes = sorted.map((a) => ({
      id: a.title,
      cluster: a.cluster,
      summary: a.summary,
      pageid: a.pageid,
    }));
    links = generateIntraClusterLinks(nodes);
  }

  const handleNodeClick = (node) => {
    const article = data.articles.find((a) => a.title === node.id);
    if (article) setSelectedArticle(article);
  };

  return (
    <div
      className="flex flex-col"
      style={{
        height: "calc(100vh - 60px)",
        backgroundColor: "#1e1e1e",
      }}
    >
      {/* Header */}
      <header className="px-6 py-3 shrink-0" style={{ borderBottom: "1px solid #3e3e42" }}>
        <h1 className="text-lg font-medium" style={{ color: "#71717a" }}>
          <span className="sr-only">Cluster visualization for </span>
          <span style={{ color: "#e4e4e7" }}>{query}</span>
          <span className="ml-2 text-sm">
            {data ? `\u2014 ${data.articles.length} articles` : ""}
          </span>
        </h1>
      </header>

      {/* Body */}
      <div className="flex flex-1 min-h-0">
        {loading && <LoadingSkeleton />}

        {error && (
          <div className="flex-1 flex items-center justify-center">
            <div
              className="rounded-lg px-6 py-4 text-sm"
              role="alert"
              style={{
                backgroundColor: "#2d1215",
                border: "1px solid #7f1d1d",
                color: "#fca5a5",
              }}
            >
              {error}
            </div>
          </div>
        )}

        {!loading && !error && data && (
          <>
            <div className="flex-1 min-w-0">
              <Graph
                nodes={nodes}
                links={links}
                onNodeClick={handleNodeClick}
              />
            </div>
            {selectedArticle && (
              <DetailSidebar
                article={selectedArticle}
                onClose={() => setSelectedArticle(null)}
              />
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default Visualize;
