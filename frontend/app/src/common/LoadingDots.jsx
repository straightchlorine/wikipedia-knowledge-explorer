const LoadingDots = () => {
    return (
        <div
            data-testid="loading-dots"
            role="status"
            aria-live="polite"
            aria-label="Loading"
            className="flex items-center justify-center gap-2 py-8"
        >
            {[0, 1, 2].map((i) => (
                <span
                    key={i}
                    aria-hidden="true"
                    className="h-3 w-3 rounded-full bg-accent-purple"
                    style={{
                        animation: "pulse 1.2s ease-in-out infinite",
                        animationDelay: `${i * 0.2}s`,
                    }}
                />
            ))}
            <span className="sr-only">Loading...</span>
            <style>{`
                @keyframes pulse {
                    0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
                    40% { opacity: 1; transform: scale(1); }
                }
            `}</style>
        </div>
    );
};

export const SkeletonCard = () => {
    return (
        <div
            className="animate-pulse rounded-xl bg-surface-700 p-5"
            aria-hidden="true"
        >
            <div className="mb-3 h-5 w-3/4 rounded bg-surface-600" />
            <div className="mb-2 h-3 w-full rounded bg-surface-600" />
            <div className="h-3 w-1/2 rounded bg-surface-600" />
        </div>
    );
};

export default LoadingDots;
