import { Link } from "react-router-dom";

const NoPage = () => (
    <div className="flex min-h-[calc(100vh-3.5rem)] flex-col items-center justify-center text-center">
        <h1 className="text-6xl font-bold text-text-muted">404</h1>
        <p className="mt-4 text-lg text-text-secondary">Page not found.</p>
        <Link
            to="/"
            className="mt-6 rounded-lg bg-accent-purple px-6 py-2 text-sm font-medium text-surface-900 hover:bg-accent-purple-hover transition-colors"
        >
            Back to Home
        </Link>
    </div>
);

export default NoPage;
