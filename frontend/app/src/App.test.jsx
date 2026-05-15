import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from './App';

vi.mock('d3', () => ({
    select: vi.fn(() => ({ selectAll: vi.fn(() => ({ remove: vi.fn() })) })),
    forceSimulation: vi.fn(() => ({ force: vi.fn().mockReturnThis(), on: vi.fn().mockReturnThis(), stop: vi.fn() })),
    forceLink: vi.fn(() => ({ id: vi.fn().mockReturnThis(), distance: vi.fn().mockReturnThis() })),
    forceManyBody: vi.fn(() => ({ strength: vi.fn().mockReturnThis() })),
    forceCenter: vi.fn(),
    forceCollide: vi.fn(() => ({ radius: vi.fn().mockReturnThis() })),
    zoom: vi.fn(() => ({ scaleExtent: vi.fn().mockReturnThis(), on: vi.fn().mockReturnThis() })),
    drag: vi.fn(() => ({ on: vi.fn().mockReturnThis() })),
    scaleOrdinal: vi.fn(() => { const fn = vi.fn(() => '#8b5cf6'); fn.domain = vi.fn(() => fn); fn.range = vi.fn(() => fn); return fn; }),
    color: vi.fn(() => ({ brighter: vi.fn(() => '#aaa') })),
    polygonHull: vi.fn(() => null),
    polygonCentroid: vi.fn(() => [0, 0]),
    easeCubicOut: (t) => t,
}));

vi.mock('./assets/logo.svg', () => ({ default: 'logo.svg' }));

global.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
};

global.fetch = vi.fn(() =>
    Promise.resolve({ ok: true, json: () => Promise.resolve({ articles: [] }) })
);

describe('App routing', () => {
    test('renders Home component on default route "/"', () => {
        render(
            <MemoryRouter initialEntries={['/']}>
                <App />
            </MemoryRouter>
        );
        expect(screen.getByText(/Explore Wikipedia Knowledge Visually/i)).toBeInTheDocument();
    });

    test('renders Explore component on "/explore"', () => {
        render(
            <MemoryRouter initialEntries={['/explore']}>
                <App />
            </MemoryRouter>
        );
        expect(screen.getByPlaceholderText(/search wikipedia/i)).toBeInTheDocument();
    });

    test('renders About component on "/about"', () => {
        render(
            <MemoryRouter initialEntries={['/about']}>
                <App />
            </MemoryRouter>
        );
        expect(screen.getByRole('heading', { name: /About the Project/i })).toBeInTheDocument();
    });

    test('renders NoPage component on invalid route', () => {
        render(
            <MemoryRouter initialEntries={['/unknown']}>
                <App />
            </MemoryRouter>
        );
        expect(screen.getByText('404')).toBeInTheDocument();
    });
});
