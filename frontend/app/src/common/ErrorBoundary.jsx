import { Component } from "react";
import { AlertTriangle, RotateCcw } from "lucide-react";

class ErrorBoundary extends Component {
    constructor(props) {
        super(props);
        this.state = { error: null };
    }

    static getDerivedStateFromError(error) {
        return { error };
    }

    componentDidCatch(error, info) {
        console.error("ErrorBoundary caught:", error, info);
    }

    handleReload = () => {
        window.location.reload();
    };

    render() {
        if (!this.state.error) return this.props.children;

        return (
            <div
                role="alert"
                className="min-h-[60vh] flex flex-col items-center justify-center gap-4 p-8 text-center"
            >
                <AlertTriangle
                    className="text-accent-purple"
                    size={48}
                    aria-hidden="true"
                />
                <h1 className="text-2xl font-semibold text-text-primary">
                    Something went wrong
                </h1>
                <p className="text-text-secondary max-w-md">
                    An unexpected error happened while rendering this page. The
                    error has been logged to the browser console.
                </p>
                <button
                    type="button"
                    onClick={this.handleReload}
                    className="inline-flex items-center gap-2 rounded-md bg-accent-purple px-4 py-2 text-white hover:bg-accent-purple-hover transition-colors"
                >
                    <RotateCcw size={16} aria-hidden="true" />
                    Reload page
                </button>
            </div>
        );
    }
}

export default ErrorBoundary;
