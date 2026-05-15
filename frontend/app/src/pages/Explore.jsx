import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Search } from "lucide-react";
import LoadingDots, { SkeletonCard } from "../common/LoadingDots";
import ErrorTag from "../common/ErrorTag";
import { apiFetch } from "../lib/api";

const ArticleCard = ({ title, summary }) => {
    const [expanded, setExpanded] = useState(false);
    const summaryId = `summary-${title.replace(/\W+/g, "-")}`;

    return (
        <article className="rounded-xl border border-surface-600/50 bg-surface-800 p-5 transition-colors hover:border-accent-purple/40">
            <h3 className="text-base font-semibold text-text-primary">{title}</h3>
            {summary && (
                <>
                    <button
                        onClick={() => setExpanded((prev) => !prev)}
                        aria-expanded={expanded}
                        aria-controls={summaryId}
                        className="mt-2 text-sm font-medium text-accent-purple hover:text-accent-purple-hover transition-colors"
                    >
                        {expanded ? "Hide Summary" : "View Summary"}
                    </button>
                    {expanded && (
                        <p
                            id={summaryId}
                            className="mt-2 text-sm leading-relaxed text-text-secondary"
                        >
                            {summary}
                        </p>
                    )}
                </>
            )}
        </article>
    );
};

const SkeletonResults = () => (
    <div
        className="mt-6 grid gap-4"
        role="status"
        aria-label="Loading search results"
    >
        {[0, 1, 2, 3].map((i) => (
            <SkeletonCard key={i} />
        ))}
        <span className="sr-only">Loading search results...</span>
    </div>
);

const Results = ({ data, query, settings }) => {
    const navigate = useNavigate();

    const handleVisualize = () => {
        navigate(`/visualize?query=${encodeURIComponent(query)}&max_results=${settings.resultCount}`);
    };

    return (
        <section className="mt-8" aria-labelledby="found-articles-heading">
            <div className="flex items-center justify-between">
                <h2
                    id="found-articles-heading"
                    className="text-lg font-semibold text-text-primary"
                >
                    Found Articles
                </h2>
                <button
                    onClick={handleVisualize}
                    className="rounded-lg bg-accent-purple px-5 py-2 text-sm font-semibold text-surface-900 transition-all hover:bg-accent-purple-hover hover:scale-105"
                >
                    Visualize Results
                </button>
            </div>
            <ul className="mt-4 grid gap-4 list-none p-0">
                {data.articles.map((item, index) => {
                    const title = typeof item === "string" ? item : item.title;
                    const summary = typeof item === "object" ? item.summary : null;
                    return (
                        <li key={index}>
                            <ArticleCard title={title} summary={summary} />
                        </li>
                    );
                })}
            </ul>
        </section>
    );
};

const DataComponent = ({ query, settings }) => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchData = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await apiFetch(
                `/api/articles/?query=${encodeURIComponent(query)}&max_results=${settings.resultCount}`
            );
            if (!response.ok) throw new Error("Failed to fetch data");
            const result = await response.json();
            setData(result);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, [query, settings]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    return (
        <div aria-live="polite" aria-busy={loading}>
            {loading && <SkeletonResults />}
            {!loading && error && (
                <div className="mt-6">
                    <ErrorTag error={error} onRetry={fetchData} />
                </div>
            )}
            {!loading && !error && data && (
                <Results data={data} query={query} settings={settings} />
            )}
        </div>
    );
};

const Explore = () => {
    const [query, setQuery] = useState("");
    const [submittedQuery, setSubmittedQuery] = useState(null);
    const [settings, setSettings] = useState({ resultCount: 5 });

    const handleSearch = (e) => {
        e.preventDefault();
        if (query.trim()) setSubmittedQuery(query.trim());
    };

    return (
        <div className="mx-auto max-w-3xl">
            <h1 className="sr-only">Search and explore Wikipedia articles</h1>

            {/* Settings */}
            <div className="mb-4 flex items-center gap-3 text-sm text-text-secondary">
                <label htmlFor="result-count">Results:</label>
                <input
                    id="result-count"
                    type="range"
                    min={1}
                    max={20}
                    value={settings.resultCount}
                    onChange={(e) =>
                        setSettings((prev) => ({
                            ...prev,
                            resultCount: Number(e.target.value),
                        }))
                    }
                    aria-valuemin={1}
                    aria-valuemax={20}
                    aria-valuenow={settings.resultCount}
                    aria-valuetext={`${settings.resultCount} ${
                        settings.resultCount === 1 ? "result" : "results"
                    }`}
                    className="w-32 accent-accent-purple"
                />
                <span
                    className="min-w-[1.5rem] text-text-primary font-medium"
                    aria-hidden="true"
                >
                    {settings.resultCount}
                </span>
            </div>

            {/* Search bar */}
            <form
                onSubmit={handleSearch}
                role="search"
                aria-label="Search Wikipedia"
                className="flex items-center gap-3 rounded-xl border border-surface-600 bg-surface-800 px-4 py-3 focus-within:border-accent-purple transition-colors"
            >
                <Search className="h-5 w-5 shrink-0 text-text-muted" aria-hidden="true" />
                <label htmlFor="search-input" className="sr-only">Search Wikipedia</label>
                <input
                    id="search-input"
                    type="text"
                    placeholder="Search Wikipedia..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    className="w-full bg-transparent text-text-primary placeholder:text-text-muted outline-none"
                />
                <button
                    type="submit"
                    className="shrink-0 rounded-lg bg-accent-purple px-4 py-1.5 text-sm font-medium text-surface-900 hover:bg-accent-purple-hover transition-colors"
                >
                    Search
                </button>
            </form>

            {submittedQuery && (
                <DataComponent query={submittedQuery} settings={settings} />
            )}
        </div>
    );
};

export default Explore;
