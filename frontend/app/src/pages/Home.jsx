import { Link } from "react-router-dom";
import { Search, Network, BarChart3 } from "lucide-react";

const features = [
    {
        icon: Search,
        title: "Search",
        description: "Query Wikipedia and retrieve relevant articles instantly.",
    },
    {
        icon: Network,
        title: "Cluster",
        description: "Group articles by similarity using K-Means clustering.",
    },
    {
        icon: BarChart3,
        title: "Visualize",
        description: "Explore topic relationships through interactive graphs.",
    },
];

const Home = () => (
    <div className="flex min-h-[calc(100vh-3.5rem)] flex-col items-center justify-center text-center">
        <div className="max-w-4xl">
            <h1 className="text-4xl font-bold tracking-tight text-text-primary md:text-5xl">
                Explore Wikipedia Knowledge Visually
            </h1>
            <p className="mt-4 text-lg text-text-secondary md:text-xl">
                Search, cluster, and visualize Wikipedia articles to discover hidden
                connections and understand topic relationships at a glance.
            </p>

            <Link
                to="/explore"
                className="mt-8 inline-block rounded-xl bg-accent-purple px-8 py-3 text-lg font-semibold text-surface-900 transition-all hover:bg-accent-purple-hover hover:scale-105"
            >
                Start Exploring
            </Link>

            <ul className="mt-16 grid gap-6 sm:grid-cols-3 list-none p-0">
                {features.map(({ icon: Icon, title, description }) => (
                    <li
                        key={title}
                        className="rounded-xl border border-surface-600/50 bg-surface-800 p-6 text-left transition-colors hover:border-accent-purple/40"
                    >
                        <Icon className="mb-3 h-8 w-8 text-accent-purple" aria-hidden="true" />
                        <h2 className="text-lg font-semibold text-text-primary">{title}</h2>
                        <p className="mt-1 text-sm text-text-secondary">{description}</p>
                    </li>
                ))}
            </ul>
        </div>
    </div>
);

export default Home;
