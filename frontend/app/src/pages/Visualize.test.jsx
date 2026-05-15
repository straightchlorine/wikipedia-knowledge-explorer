import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import Visualize from './Visualize';
import { generateIntraClusterLinks } from '../components/Graph';

vi.mock('d3', () => {
    const chainable = () => {
        const obj = {};
        const handler = {
            get(target, prop) {
                if (prop in target) return target[prop];
                target[prop] = vi.fn(() => new Proxy({}, handler));
                return target[prop];
            },
        };
        return new Proxy(obj, handler);
    };
    return {
        select: () => chainable(),
        forceSimulation: () => chainable(),
        forceLink: () => chainable(),
        forceManyBody: () => chainable(),
        forceCenter: vi.fn(),
        forceCollide: () => chainable(),
        zoom: () => chainable(),
        drag: () => chainable(),
        scaleOrdinal: () => {
            const fn = vi.fn(() => '#8b5cf6');
            fn.domain = vi.fn(() => fn);
            fn.range = vi.fn(() => fn);
            return fn;
        },
        color: vi.fn(() => ({ brighter: vi.fn(() => '#aaa') })),
        polygonHull: vi.fn(() => null),
        polygonCentroid: vi.fn(() => [0, 0]),
        easeCubicOut: (t) => t,
    };
});

global.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
};

global.fetch = vi.fn(() =>
    Promise.resolve({
        ok: true,
        json: () =>
            Promise.resolve({
                query: 'test',
                articles: [
                    { title: 'A1', pageid: 1, cluster: 0, summary: 'Summary A1' },
                    { title: 'A2', pageid: 2, cluster: 0, summary: 'Summary A2' },
                    { title: 'B1', pageid: 3, cluster: 1, summary: 'Summary B1' },
                ],
            }),
    })
);

function renderWithRoute(url) {
    return render(
        <MemoryRouter initialEntries={[url]}>
            <Routes>
                <Route path="/visualize" element={<Visualize />} />
            </Routes>
        </MemoryRouter>
    );
}

describe('generateIntraClusterLinks', () => {
    test('creates links within clusters, not between them', () => {
        const nodes = [
            { id: 'A1', cluster: 0 },
            { id: 'A2', cluster: 0 },
            { id: 'B1', cluster: 1 },
            { id: 'B2', cluster: 1 },
        ];
        const links = generateIntraClusterLinks(nodes);

        expect(links).toContainEqual({ source: 'A1', target: 'A2' });
        expect(links).toContainEqual({ source: 'B1', target: 'B2' });

        const crossCluster = links.filter(
            (l) =>
                (l.source.startsWith('A') && l.target.startsWith('B')) ||
                (l.source.startsWith('B') && l.target.startsWith('A'))
        );
        expect(crossCluster).toHaveLength(0);
    });

    test('fully connects small clusters (<=5 nodes)', () => {
        const nodes = [
            { id: 'N1', cluster: 0 },
            { id: 'N2', cluster: 0 },
            { id: 'N3', cluster: 0 },
        ];
        const links = generateIntraClusterLinks(nodes);
        expect(links).toHaveLength(3);
    });
});

describe('Visualize page', () => {
    test('shows loading state initially', () => {
        renderWithRoute('/visualize?query=test&max_results=10');
        expect(screen.getByText(/Clustering articles/i)).toBeInTheDocument();
    });

    test('shows query in header after data loads', async () => {
        renderWithRoute('/visualize?query=test&max_results=10');
        await waitFor(() => {
            expect(screen.getByText('test')).toBeInTheDocument();
        });
    });

    test('shows error message if fetch fails', async () => {
        fetch.mockImplementationOnce(() => Promise.resolve({ ok: false }));

        renderWithRoute('/visualize?query=fail&max_results=10');

        await waitFor(() => {
            expect(screen.getByText(/Failed to fetch cluster data/i)).toBeInTheDocument();
        });
    });

    test('renders without crashing when no query param', () => {
        renderWithRoute('/visualize');
        expect(document.body).toBeTruthy();
    });
});
