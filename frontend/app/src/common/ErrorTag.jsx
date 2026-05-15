import { AlertCircle } from "lucide-react";

const ErrorTag = ({ error, onRetry }) => {
    return (
        <div
            role="alert"
            className="flex items-center gap-3 rounded-lg border border-error/30 bg-error/10 px-4 py-3"
        >
            <AlertCircle className="h-5 w-5 shrink-0 text-error" aria-hidden="true" />
            <p className="text-sm text-error">{error}</p>
            {onRetry && (
                <button
                    onClick={onRetry}
                    className="ml-auto shrink-0 rounded-md bg-error/20 px-3 py-1 text-sm text-error hover:bg-error/30 transition-colors"
                >
                    Retry
                </button>
            )}
        </div>
    );
};

export default ErrorTag;
