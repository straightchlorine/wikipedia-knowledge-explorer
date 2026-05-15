import { Github } from "lucide-react";

const techStack = [
    "React", "FastAPI", "D3.js", "SentenceTransformer",
    "BART", "K-Means", "Docker", "Kubernetes",
];

const About = () => (
    <section className="mx-auto max-w-3xl">
        <h1 className="text-3xl font-bold text-text-primary">About the Project</h1>

        <p className="mt-4 text-text-secondary leading-relaxed">
            <strong className="text-text-primary">Wikipedia Knowledge Explorer</strong> is
            an interactive tool that helps users explore and understand related topics on
            Wikipedia through intelligent clustering, summarization, and visualization.
        </p>

        <p className="mt-3 text-text-secondary leading-relaxed">
            The application retrieves related articles, clusters them based on content
            similarity using sentence embeddings, summarizes key information with BART, and
            visualizes the results in an interactive graph interface.
        </p>

        <h2 className="mt-10 text-xl font-semibold text-text-primary">Tech Stack</h2>
        <div className="mt-4 flex flex-wrap gap-2">
            {techStack.map((tech) => (
                <span
                    key={tech}
                    className="rounded-full border border-surface-600 bg-surface-800 px-3 py-1 text-sm text-text-secondary"
                >
                    {tech}
                </span>
            ))}
        </div>

        <a
            href="https://github.com/straightchlorine/wikipedia-knowledge-explorer"
            target="_blank"
            rel="noopener noreferrer"
            className="mt-8 inline-flex items-center gap-2 text-accent-purple hover:text-accent-purple-hover transition-colors"
        >
            <Github className="h-5 w-5" aria-hidden="true" />
            <span className="text-sm font-medium">View on GitHub</span>
            <span className="sr-only">(opens in new tab)</span>
        </a>
    </section>
);

export default About;
